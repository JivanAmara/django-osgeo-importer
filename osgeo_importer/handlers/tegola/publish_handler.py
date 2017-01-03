from logging import getLogger
import os

from django.conf import settings
import toml

from osgeo_importer.handlers import ImportHandlerMixin
from osgeo_importer.models import UploadLayer, TegolaLayerConfig


logger = getLogger(__name__)


class TegolaVectorDataPublishHandler(ImportHandlerMixin):
    def handle(self, layer, layer_config, *args, **kwargs):
        if layer_config.get('layer_type') == 'vector':
            tegola_port = settings.TEGOLA_PORT if hasattr(settings, 'TEGOLA_PORT') else 9090

            postgis_table_name = layer
            postgis_db_host = settings.DATABASES['datastore']['HOST']
            postgis_db_port = settings.DATABASES['datastore']['PORT']
            postgis_db_name = settings.DATABASES['datastore']['NAME']
            postgis_user = settings.DATABASES['datastore']['USER']
            postgis_pass = settings.DATABASES['datastore']['PASSWORD']
            layer_name = layer_config.get('layer_name', 'no layer name')
            srs = layer_config.get('srs')
            srid = int(srs.split(':')[-1])  # Take an srs like "EPSG:4326" and return only the id number
            geometry_field_name = 'wkb_geometry'
            geometry_id_field_name = 'ogc_fid'

            provider_config = {
                'name': "geonode_postgis",  # provider name is referenced from map layers
                'type': "postgis",  # the type of data provider. currently only supports postgis
                'host': postgis_db_host,  # postgis database host
                'port': postgis_db_port,  # postgis database port
                'database': postgis_db_name,  # postgis database name
                'user': postgis_user,  # postgis database user
                'password': postgis_pass,  # postgis database password
                'srid': srid,  # The default srid for this provider. If not provided it will be WebMercator (3857)
            }

            layer_config = {
                'name': layer_name,  # will be encoded as the layer name in the tile
                'tablename': postgis_table_name,  # sql or table_name are required
                'geometry_fieldname': geometry_field_name,  # geom field. default is geom
                'id_fieldname': geometry_id_field_name,  # geom id field. default is gid
                'srid': 4326,  # the srid of table's geo data.
            }

            uploaded_layer = UploadLayer.objects.get(layer_name=layer_name)
            layer_toml_config = toml.dumps(layer_config)
            TegolaLayerConfig.objects.create(layer=uploaded_layer, config=layer_toml_config)

            layer_configs = [toml.loads(tlc.config) for tlc in TegolaLayerConfig.objects.all()]
            provider_config['layers'] = [lc for lc in layer_configs]
            config = {
                'providers': [provider_config]
            }

            toml_config = toml.dumps(config)
            config_filepath = os.path.join(settings.TEGOLA_CONFIG_DIR, settings.TEGOLA_CONFIG_FILENAME)
            with open(config_filepath, 'w') as f:
                f.write(toml_config)
#             db_engine_import = settings.DATABASES['datastore']['ENGINE']
#             db_engine_name = db_engine_import.split('.')[-1]
        else:
            logger.info('Layer: "{}" is not a vector layer, ignoring it.'.format(layer_config.get('name')))
