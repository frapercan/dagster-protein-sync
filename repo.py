import logging
from datetime import timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dagster import op, job, ScheduleDefinition

from protein_data_handler.helpers.config.yaml import read_yaml_config
from protein_data_handler.models.uniprot import Base, PDBReference
from protein_data_handler.uniprot import cargar_codigos_acceso, extraer_entradas
from protein_data_handler.pdb import download_entire_pdb
from protein_data_handler.fasta import FastaHandler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_database_session():
    config = read_yaml_config("./config/config.yaml")
    database_uri = (f"postgresql+psycopg2://{config['DB_USERNAME']}:"
                    f"{config['DB_PASSWORD']}"
                    f"@{config['DB_HOST']}:"
                    f"{config['DB_PORT']}/"
                    f"{config['DB_NAME']}")
    engine = create_engine(database_uri)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


@op
def cargar_codigos_op():
    """Carga códigos de acceso de UniProt."""
    session = get_database_session()
    config = read_yaml_config("./config/config.yaml")
    cargar_codigos_acceso(criterio_busqueda=config['criterio_busqueda'], limite=config['limit'], session=session)


@op
def procesar_datos_uniprot_op(cargar_codigos):
    """Procesa datos de UniProt."""
    session = get_database_session()
    extraer_entradas(session=session)


@op
def descargar_pdb_op():
    config = read_yaml_config("./config/config.yaml")
    server = config['server']
    pdb = config['pdb']
    file_format = config['file_format']
    download_entire_pdb(server, pdb, file_format)


def initialize_fasta_handler(config):
    session = get_database_session()
    return FastaHandler(session, config['data_dir'], config['output_dir'])


@op
def descargar_mergear_fastas_op(procesar_datos_uniprot_op):
    """
    Operación para descargar archivos FASTA.
    """
    config = read_yaml_config("./config/config.yaml")
    fasta_handler = initialize_fasta_handler(config)
    logging.info("Descargando archivos FASTA...")
    session = get_database_session()
    query = session.query(PDBReference).filter(PDBReference.resolution < config.get("resolution_threshold", 2.5)).all()
    pdb_ids = [pdb_ref.pdb_id for pdb_ref in query]
    # Inicializa FastaHandler
    fasta_downloader = FastaHandler(session, config['data_dir'], config['output_dir'])

    # Descarga los archivos FASTA
    fasta_downloader.download_fastas(pdb_ids, config['max_workers'])

    fasta_downloader.merge_fastas(pdb_ids, config['merge_name'])


@job
def protein_data_pipeline():
    descargar_mergear_fastas_op(procesar_datos_uniprot_op(cargar_codigos_op()))
    descargar_pdb_op()


# Programar la ejecución del trabajo cada 8 días
protein_data_schedule = ScheduleDefinition(
    job=protein_data_pipeline,
    cron_schedule="0 0 */8 * *",  # Esto ejecutará el trabajo a medianoche cada 8 días
)
