#!/bin/env python
# -*- coding: utf-8 -*-
from ..lib import utils
from pyramid_restler.view import RESTfulView
from pyramid.response import Response
from pyramid.exceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPFound


def response_callback(request, response):
    #response.headerlist.append(('x', 'y'))
    try:
        if request.context.session.is_active:
            request.context.session.close()
    except:
        pass

    if 'callback' in request.params:
        response.text = request.params['callback'] + '(' + response.text + ')'


class CustomView(RESTfulView):

    """ Default Customized View Methods
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.request.add_response_callback(response_callback)
        self.base_name = self.request.matchdict.get('base')

    def get_base(self):
        """ Return Base object
        """
        return self.context.get_base()

    def set_base(self, base_json):
        """ Set Base object
        """
        return self.context.set_base(base_json)

    def get_collection(self, render_to_response=True):
        """ Search database objects
        """
        params = self.request.params.get('$$', '{}')
        query = utils.json2object(params)
        try:
            collection = self.context.get_collection(query)
        except Exception as e:
            raise Exception('SearchError: %s' % e)
        else:
            if render_to_response:
                response = self.render_to_response(collection)
            else:
                response = collection
        return response

    def get_member(self):
        id = self.request.matchdict['id']
        self.wrap = False
        member = self.context.get_member(id)
        return self.render_to_response(member)

    def create_member(self):
        member = self.context.create_member(self._get_data())
        id = self.context.get_member_id_as_string(member)
        return self.render_custom_response(id, default_response=id)

    def update_member(self):
        id = self.request.matchdict['id']
        member = self.context.get_member(id, close_sess=False)
        if member is None:
            raise HTTPNotFound()
        self.context.update_member(member, self._get_data(member))
        return self.render_custom_response(id, default_response='UPDATED')

    def delete_member(self):
        id = self.request.matchdict['id']
        member = self.context.delete_member(id)
        if member is None:
            raise HTTPNotFound()
        return Response('DELETED', charset='utf-8', status=200, content_type='')

    def render_custom_response(self, id, default_response):
        _return = self.request.params.get('return', '')
        is_valid_return = hasattr(self.context.entity, _return)
        if is_valid_return:
            member = self.context.get_member(id)
            response_attr = getattr(member, _return)
            return Response(str(response_attr), charset='utf-8', status=200, content_type='application/json')
        else:
            return Response(default_response, charset='utf-8', status=200, content_type='')

    def get_collection_cached(self, render_to_response=True):
        """
        Return document collection in cache

        :param render_to_response: Should we render or return JSON
        :return: Document HTML or JSON
        """
        params = self.request.params.get('$$', '{}')

        # Cache key concerning expiring time
        cache_type = self.request.params.get('cache_key', 'default_term')
        cache_key = self.request.current_route_path()
        query = utils.json2object(params)
        try:
            collection = self.context.get_collection_cached(query, cache_key, cache_type)
        except Exception as e:
            raise Exception('SearchError: %s' % e)
        else:
            if render_to_response:
                response = self.render_to_response(collection)
            else:
                response = collection
        return response

    def get_member_cached(self):
        """
        Get member cached
        :return:
        """
        id = self.request.matchdict['id']
        cache_key = self.request.current_route_path()
        self.wrap = False
        # Get cached member
        member = self.context.get_member_cached(id, cache_key)
        return self.render_to_response(member)