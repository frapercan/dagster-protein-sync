import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dagster import asset

from protein_data_handler.helpers.config.yaml import read_yaml_config
from protein_data_handler.models.uniprot import Base
from protein_data_handler.uniprot import cargar_codigos_acceso, extraer_entradas

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')




@asset
def cargar_codigos():
    """Carga códigos de acceso de UniProt."""
    config = read_yaml_config("../config/config.yaml")
    database_uri = (f"postgresql+psycopg2://{config['DB_USERNAME']}:"
                    f"{config['DB_PASSWORD']}"
                    f"@{config['DB_HOST']}:"
                    f"{config['DB_PORT']}/"
                    f"{config['DB_NAME']}")
    engine = create_engine(database_uri)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    cargar_codigos_acceso(criterio_busqueda=config['criterio_busqueda'], limite=config['limit'], session=Session())


@asset(deps=[cargar_codigos])
def procesar_datos_uniprot():
    """Procesa datos de UniProt."""
    config = read_yaml_config("../config/config.yaml")
    database_uri = (f"postgresql+psycopg2://{config['DB_USERNAME']}:"
                    f"{config['DB_PASSWORD']}"
                    f"@{config['DB_HOST']}:"
                    f"{config['DB_PORT']}/"
                    f"{config['DB_NAME']}")
    engine = create_engine(database_uri)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    extraer_entradas(session=Session())


