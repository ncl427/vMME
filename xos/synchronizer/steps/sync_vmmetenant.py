# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
from django.db.models import Q, F
#from services.vmme.models import VMMEService, VMMETenant
from synchronizers.new_base.modelaccessor import *
from synchronizers.new_base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)

class SyncVMMETenant(SyncInstanceUsingAnsible):

    provides = [VMMETenant]

    observes = VMMETenant

    requested_interval = 0

    template_name = "vmmetenant_playbook.yaml"

    service_key_name = "/opt/xos/configurations/mcord/mcord_private_key"

    def __init__(self, *args, **kwargs):
        super(SyncVMMETenant, self).__init__(*args, **kwargs)

    def get_network_id(self, network_name):
        network = Network.objects.filter(name=network_name).first()

        return network.id

    def get_instance_object(self, instance_id):
        instance = Instance.objects.filter(id=instance_id).first()

        return instance

    def get_spgwc_list(self):
        vspgwc_list = VSPGWCTenant.objects.all()
        vspgwc_idlist = map(lambda x: x.instance_id, vspgwc_list)

        spgwc = filter(lambda x: x.id in vspgwc_idlist, Instance.objects.all())
        spgwc_network = self.get_network_id('vspgwc_network')

        spgwc_iplist = []

        for obj in spgwc:
            port = filter(lambda x: x.network_id == spgwc_network, obj.ports.all())[0]
            spgwc_iplist.append(port.ip)

        return spgwc_iplist

    def get_information(self, o):
        fields = {}

        collect_network = [
           {'name': 'MME_PRIVATE_IP', 'net_name': 'vmme_network'}        
        ]

        instance = self.get_instance_object(o.instance_id)

        for data in collect_network:
            network_id = self.get_network_id(data['net_name'])
            port = filter(lambda x: x.network_id == network_id, instance.ports.all())[0]
            fields[data['name']] = port.ip

        fields["SPGWC_IP_LIST"] = self.get_spgwc_list()

        return fields

    def get_extra_attributes(self, o):
        fields = self.get_information(o)

        return fields
