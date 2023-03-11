import glob
import logging
import re
from flask import Flask, render_template

GLOBAL_DATA = {}
app = Flask(__name__)
WEKZEUG_LOG = logging.getLogger('werkzeug')
WEKZEUG_LOG.disabled = True

def get_subdomain_confs():
    path = r'/proxy-confs/*.subdomain.conf'
    return glob.glob(path)


def get_conf_contents(conf_file_path):
    with open(conf_file_path, "r") as f:
        contents = f.read()
    return contents


def parse_conf_configuration(conf_contents):
    data = {"locations": {}}

    # Server Portion
    LOCATION_SEC_EXPR = r'\s* location\s(\S+)\s{([^}]*)}'
    SERVER_NAME_EXPR = r'^\s*server_name\s(\S+)\.\*;\s*$'
    AUTHELIA_SERVER_ENABLED_EXPR = r'^\s*include\s\/config\/nginx\/authelia-server\.conf;\s*$'
    BLOCK_EXTERNAL_ACCESS_ENABLED_EXPR = r'^\s*allow\s([0-9]{1,3}\.){3}[0-9]{1,3}($|/(16|24));\s*$\s*deny\sall;\s*$'

    # Location Portion
    AUTHELIA_LOCATION_ENABLED_EXPR = r'^\s*include\s\/config\/nginx\/authelia-location\.conf;\s*$'
    UPSTREAM_APP_EXPR = r'^\s*set\s\$upstream_app\s(\S+);\s*$'
    UPSTREAM_PORT_EXPR = r'^\s*set\s\$upstream_port\s(\S+);\s*$'
    UPSTREAM_PROTO_EXPR = r'^\s*set\s\$upstream_proto\s(\S+);\s*$'

    server_portion = re.sub(LOCATION_SEC_EXPR, "", conf_contents)
    location_portions = {loc_name: loc_contents for loc_name, loc_contents in re.findall(LOCATION_SEC_EXPR, conf_contents, re.MULTILINE)}

    # Server Portion
    subdomain = re.search(SERVER_NAME_EXPR, server_portion, re.MULTILINE)
    data['subdomain'] = subdomain[1] if subdomain is not None else None

    authelia_enabled = re.search(AUTHELIA_SERVER_ENABLED_EXPR, server_portion, re.MULTILINE)
    data['authelia'] = True if authelia_enabled is not None else False

    external_access_blocked = re.search(BLOCK_EXTERNAL_ACCESS_ENABLED_EXPR, server_portion, re.MULTILINE)
    data['external_access'] = False if external_access_blocked is not None else True

    # Location Section
    for location_name, location_config in location_portions.items():
        location_data = {}

        authelia_loc_enabled = re.search(AUTHELIA_LOCATION_ENABLED_EXPR, location_config, re.MULTILINE)
        location_data['authelia'] = True if authelia_loc_enabled is not None else False

        upstream_app = re.search(UPSTREAM_APP_EXPR, location_config, re.MULTILINE)
        location_data['upstream_app'] = upstream_app[1] if upstream_app is not None else None

        upstream_port = re.search(UPSTREAM_PORT_EXPR, location_config, re.MULTILINE)
        location_data['upstream_port'] = upstream_port[1] if upstream_port is not None else None

        upstream_proto = re.search(UPSTREAM_PROTO_EXPR, location_config, re.MULTILINE)
        location_data['upstream_proto'] = upstream_proto[1] if upstream_proto is not None else None
        data["locations"][location_name] = location_data
    return data


def get_cls(value):
    return ""


@app.route('/')
def index():
    table_rows = []
    ["<tr><th>Service</th><th>Location</th><th>External Access</th><th>Authelia</th></tr>"]
    for conf_loc, service_data in GLOBAL_DATA.items():
        for location, location_data in service_data["locations"].items():
            table_rows.append({
                "subdomain": service_data["subdomain"],
                "location": location,
                "external_access": "Enabled" if service_data["external_access"] else "Disabled",
                "location_authelia": "Enabled" if service_data["authelia"] else "Disabled")
            })
    return render_template('index.html', table_rows=table_rows)

if __name__ == "__main__":
    conf_locations = get_subdomain_confs()
    for conf_location in conf_locations:
        conf_contents = get_conf_contents(conf_location)
        GLOBAL_DATA[conf_location] = parse_conf_configuration(conf_contents)
    print(GLOBAL_DATA)

    print(f"Starting Flask @ http://localhost:8025")
    app.run(host='0.0.0.0', port=8025)
