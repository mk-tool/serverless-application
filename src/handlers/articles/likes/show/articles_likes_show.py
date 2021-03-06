# -*- coding: utf-8 -*-
import json
import os
import settings
from db_util import DBUtil
from lambda_base import LambdaBase
from jsonschema import validate, ValidationError
from boto3.dynamodb.conditions import Key
from decimal_encoder import DecimalEncoder


class ArticlesLikesShow(LambdaBase):
    def get_schema(self):
        return {
            'type': 'object',
            'properties': {
                'article_id': settings.parameters['article_id']
            },
            'required': ['article_id']
        }

    def validate_params(self):
        # single
        if self.event.get('pathParameters') is None:
            raise ValidationError('pathParameters is required')
        validate(self.event.get('pathParameters'), self.get_schema())
        # relation

        DBUtil.validate_article_existence(
            self.dynamodb,
            self.event['pathParameters']['article_id'],
            status='public'
        )

    def exec_main_proc(self):
        query_params = {
            'KeyConditionExpression': Key('article_id').eq(self.event['pathParameters']['article_id']),
            'Select': 'COUNT'
        }
        article_liked_user_table = self.dynamodb.Table(os.environ['ARTICLE_LIKED_USER_TABLE_NAME'])
        response = article_liked_user_table.query(**query_params)

        return {
            'statusCode': 200,
            'body': json.dumps({'count': response['Count']}, cls=DecimalEncoder)
        }
