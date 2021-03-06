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
import uuid

import webob

import glance.common.context
from glance.common import exception

LOG = logging.getLogger(__name__)

UUID1 = 'c80a1a6c-bd1f-41c5-90ee-81afedb1d58d'
UUID2 = '971ec09a-8067-4bc8-a91f-ae3557f1c4c7'

TENANT1 = '6838eb7b-6ded-434a-882c-b344c77fe8df'
TENANT2 = '2c014f32-55eb-467d-8fcb-4bd706012f81'

USER1 = '54492ba0-f4df-4e4e-be62-27f4d76b29cf'
USER2 = '0b3b3006-cb76-4517-ae32-51397e22c754'


class FakeRequest(webob.Request):
    def __init__(self):
        #TODO(bcwaldon): figure out how to fake this out cleanly
        super(FakeRequest, self).__init__({'REQUEST_METHOD': 'POST'})

        kwargs = {
            'user': USER1,
            'tenant': TENANT1,
            'roles': [],
            'is_admin': False,
        }
        self.context = glance.common.context.RequestContext(**kwargs)


class FakeDB(object):

    def __init__(self):
        self.images = {
            UUID1: self._image_format(UUID1),
            UUID2: self._image_format(UUID2),
        }
        self.members = {
            UUID1: [
                self._image_member_format(UUID1, TENANT1, True),
                self._image_member_format(UUID1, TENANT2, False),
            ],
            UUID2: [],
        }

    def reset(self):
        self.images = {}
        self.members = {}

    def configure_db(*args, **kwargs):
        pass

    def _image_member_format(self, image_id, tenant_id, can_share):
        return {
            'image_id': image_id,
            'member': tenant_id,
            'can_share': can_share,
        }

    def _image_format(self, image_id, **values):
        image = {'id': image_id, 'name': 'image-name'}
        image.update(values)
        return image

    def image_get(self, context, image_id):
        try:
            image = self.images[image_id]
            LOG.info('Found image %s: %s' % (image_id, str(image)))
        except KeyError:
            raise exception.NotFound(image_id=image_id)

        #NOTE(bcwaldon: this is a hack until we can get image members with
        # a direct db call
        image['members'] = self.members.get(image_id, [])

        return image

    def image_get_all(self, context, filters=None):
        return self.images.values()

    def image_member_find(self, context, image_id, tenant_id):
        try:
            self.images[image_id]
        except KeyError:
            raise exception.NotFound()

        for member in self.members.get(image_id, []):
            if member['member'] == tenant_id:
                return member

        raise exception.NotFound()

    def image_member_create(self, context, values):
        member = self._image_member_format(values['image_id'],
                                           values['member'],
                                           values['can_share'])
        self.members[values['image_id']] = member
        return member

    def image_create(self, context, image_values):
        new_uuid = str(uuid.uuid4())
        image = self._image_format(new_uuid, **image_values)
        self.images[new_uuid] = image
        LOG.info('Created image %s with values %s' %
                 (new_uuid, str(image_values)))
        return image

    def image_update(self, context, image_id, image_values):
        LOG.info('Updating image %s with values %s' %
                 (image_id, str(image_values)))
        try:
            image = self.images[image_id]
            LOG.info('Found image %s: %s' % (image_id, str(image)))
        except KeyError:
            raise exception.NotFound(image_id=image_id)

        image.update(image_values)
        self.images[image_id] = image
        LOG.info('Image %s updated to %s' % (image_id, str(image)))
        return image
