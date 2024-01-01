from pony.orm import Database

import system_settings
from database import models, db_services

# zum Deployen müssen server_remote_access, local und from_outside False sein
server_remote_access = False
local = True  # True: sqlite-database, False: postgresql-database
from_outside = False  # False: calling database from same API

# sql_debug(True)


def generate_db_mappings(db: Database, file: str):

    if not local:
        #########################################################################################################
        # this ist the connection to postgresql on render.com
        if from_outside:
            host = f'{system_settings.settings.settings.host_sql}.frankfurt-postgres.render.com'
        else:
            host = system_settings.settings.host_sql
        db.bind(provider=system_settings.settings.provider_sql,
                user=system_settings.settings.user_sql,
                password=system_settings.settings.password_sql,
                host=host, database=system_settings.settings.database_sql)
        ##########################################################################################################
    else:
        provider = system_settings.settings.provider

        db.bind(provider=provider, filename=file, create_db=True)

    db.generate_mapping(create_tables=True)


def start_db():
    if not server_remote_access:
        for db, file in ((models.db_clown_control, system_settings.settings.db_clown_control),):
            generate_db_mappings(db=db, file=file)
