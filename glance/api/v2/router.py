# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

import routes

from glance.api.v2 import images
from glance.api.v2 import root
from glance.api.v2 import schemas
from glance.common import wsgi

logger = logging.getLogger(__name__)


class API(wsgi.Router):

    """WSGI router for Glance v2 API requests."""

    def __init__(self, conf, **local_conf):
        self.conf = conf
        mapper = routes.Mapper()

        root_resource = root.create_resource(conf)
        mapper.connect('/', controller=root_resource, action='index')

        schemas_resource = schemas.create_resource(conf)
        mapper.connect('/schemas',
                       controller=schemas_resource,
                       action='index',
                       conditions={'method': ['GET']})
        mapper.connect('/schemas/image',
                       controller=schemas_resource,
                       action='image',
                       conditions={'method': ['GET']})
        mapper.connect('/schemas/image/access',
                       controller=schemas_resource,
                       action='access',
                       conditions={'method': ['GET']})

        images_resource = images.create_resource(conf)
        mapper.connect('/images',
                       controller=images_resource,
                       action='index',
                       conditions={'method': ['GET']})
        mapper.connect('/images',
                       controller=images_resource,
                       action='create',
                       conditions={'method': ['POST']})
        mapper.connect('/images/{image_id}',
                       controller=images_resource,
                       action='update',
                       conditions={'method': ['PUT']})
        mapper.connect('/images/{image_id}',
                       controller=images_resource,
                       action='show',
                       conditions={'method': ['GET']})
        mapper.connect('/images/{image_id}',
                       controller=images_resource,
                       action='delete',
                       conditions={'method': ['DELETE']})

        super(API, self).__init__(mapper)
