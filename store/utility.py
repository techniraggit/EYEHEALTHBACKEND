import json

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from accounts.models import Store
from core.s3access import S3Access
from store.models import StoreDetail, StoreAvail, Days, Timing, Holiday, StoreHoliday
from utilities.elastic import ElasticIndex


def store_file_upload_handle(store_id, store_images, *args, **kwargs) -> dict:
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    server_file_loc = "shared/store_imgs"
    s3_base_url = f'https://s3.ap-south-1.amazonaws.com/{bucket_name}/{server_file_loc}'

    local_file_loc = settings.PROJECT_DIR + '/store_imgs/'
    response = dict()

    server_file_loc = "shared/store_imgs/"

    for key, val in store_images.items():
        file_name = val.name.replace(' ', '_')

        if kwargs.get('put'):
            store_pk = store_id
        elif kwargs.get('post'):
            store_pk = store_id + 1
        new_filename = f"store_{store_pk}_{key}.{file_name.split('.')[-1]}"
    
        fs = FileSystemStorage(str(local_file_loc))
        file_name = fs.save(new_filename, val)

        uploaded_file_url = fs.url(file_name)
        uploaded_file_url = str(uploaded_file_url).replace('/media', '')
        response[key] = s3_base_url + uploaded_file_url
        local_file_path = fs.location + "/" + file_name
        server_file_path = server_file_loc + file_name

        s3_access = S3Access(bucket_name=bucket_name, local_file_path=local_file_path, server_file_path=server_file_path)
        if s3_access.upload_file():
            fs.delete(file_name)

    return response


def get_data_store_data_for_elastic():
    """
    StoreAvail.objects.select_related('store', 'day', 'timing', 'store__storedetail').values_list('store_id', 'store__store_name', 'store__store_image', 'store__store_code', 'store__pin_code', 'store__city', 'store__country', 'store__landmark', 'store__storedetail__location', 'store__storedetail__phone', 'store__storedetail__services', 'timing__start_time', 'timing__end_time', 'day__day')
    response:
    {'id': 36, 'store_name': 'mona shop', 'store_code': '1237654', 'store_image': '/media/Store/store_image/download_1_mBPLkbL.jpg', 'address': 'majitha raod', 'landmark': 'nehru colony', 'country': 'India', 'pin_code': 143001, 'state': 'PUNJAB', 'city': 'AMRITSAR', 'phone': 7752882952, 'description': 'Testing Store Details', 'location': {'latitude': 100.0, 'longitude': 80.0}, 'services': [{'name': 'Anti Fog Spray', 'is_paid': False}, {'name': 'Eye Test', 'is_paid': False}], 'Availability': [{'Monday': {'start_time': datetime.time(9, 0), 'end_time': datetime.time(18, 0)}}, {'Tuesday': {'start_time': datetime.time(9, 0), 'end_time': datetime.time(18, 0)}}, {'Wednesday': {'start_time': datetime.time(9, 0), 'end_time': datetime.time(18, 0)}}, {'Thursday': {'start_time': datetime.time(9, 0), 'end_time': datetime.time(18, 0)}}, {'Friday': {'start_time': datetime.time(9, 0), 'end_time': datetime.time(18, 0)}}, {'Saturday': {'start_time': datetime.time(10, 0), 'end_time': datetime.time(19, 0)}}, {'Sunday': {'start_time': datetime.time(10, 0), 'end_time': datetime.time(19, 0)}}], 'holidays': [{'name': 'New Year', 'type': 'RESTRICTED', 'date': datetime.date(2024, 1, 1)}, {'name': 'Republic Day', 'type': 'NATIONAL', 'date': datetime.date(2024, 1, 26)}]}
    """
    data = []
    sts = Store.objects.filter(is_active=True)
    for st in sts:
        store_dict = {}
        store_dict.update(
            {'id': st.pk, 'store_name': st.store_name, 'store_code': st.store_code, 'store_image': '',
             'address': st.address, 'landmark': st.landmark, 'country': st.country, 'pin_code': int(st.pin_code),
             'state': st.state, 'city': st.city, 'locality': st.locality})
        sd = StoreDetail.objects.filter(store=st).first()
        if sd:
            location = json.loads(sd.location.json)
            store_dict.update({'phone': int(sd.phone), 'description': sd.description})
            store_dict['location'] = "{0},{1}".format(location['coordinates'][0], location['coordinates'][1])
            store_dict['services'] = [{'name': service.service, 'is_paid': service.is_paid} for service in sd.services.all()]
            sas = StoreAvail.objects.filter(store=st).all()
            avail = {}
            for sa in sas:
                d = Days.objects.filter(pk=sa.day_id).first()
                t = Timing.objects.filter(pk=sa.timing_id).first()
                avail[d.day] = {'start_time': t.start_time.isoformat(), 'end_time': t.end_time.isoformat()}
            store_dict['Availability'] = avail

            hs = StoreHoliday.objects.filter(store=st).values_list('id')
            hss = Holiday.objects.filter(pk__in=hs)
            store_dict['holidays'] = {str(i.date): {'name': i.name, 'type': i.type} for i in hss}

        data.append(store_dict)
    return data


class IndexStore(ElasticIndex):

    def gen_data(self, index_name):
        stores = get_data_store_data_for_elastic()
        for store in stores:
            # yield {
            #     "_index": index_name,
            #     "_id": store['id'],
            #     "store": store,
            # }
            yield {
                "_index": index_name,
                "_id": store['id'],
                **store,
            }

    def create_index(self, name):
        '''
        Add field to list to add mapping to setting
                            # "location": {
                    #     "type": "object",
                    #     "properties": {
                    #         "latitude": {"type": "float"},
                    #         "longitude": {"type": "float"},
                    #     }
                    # },
        '''
        string_to_index = ["stores"]

        str_mapping = {
            "type": "text",
            "index_options": "offsets",
            "fields": {
                "delimiter": {
                    "type": "text",
                    "term_vector": "with_positions_offsets",
                    "index_options": "offsets",
                    "analyzer": "iq_text_delimiter",
                    "position_increment_gap": 100
                },
                "enum": {
                    "type": "keyword",
                    "ignore_above": 2048
                },
                "intragram": {
                    "type": "text",
                    "index_options": "docs",
                    "analyzer": "iq_intragram"
                },
                "joined": {
                    "type": "text",
                    "term_vector": "with_positions_offsets",
                    "index_options": "offsets",
                    "analyzer": "iq_text_bigram",
                    "position_increment_gap": 100
                },
                "prefix": {
                    "type": "text",
                    "term_vector": "with_positions_offsets",
                    "index_options": "docs",
                    "analyzer": "i_prefix",
                    "search_analyzer": "q_prefix"
                },
                "stem": {
                    "type": "text",
                    "term_vector": "with_positions_offsets",
                    "index_options": "offsets",
                    "analyzer": "iq_text_stem",
                    "position_increment_gap": 100
                }
            },
            "analyzer": "iq_text_base",
            "position_increment_gap": 100
        }

        string_mappings = {s: str_mapping for s in string_to_index}
        index_settings = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "store_name": {"type": "text"},
                    "store_code": {"type": "text"},
                    "store_image": {"type": "text"},
                    "address": {"type": "text"},
                    "landmark": {"type": "text"},
                    "locality": {"type": "text"},
                    "country": {"type": "text"},
                    "pin_code": {"type": "keyword"},
                    "state": {"type": "text"},
                    "city": {"type": "text"},
                    "phone": {"type": "long"},
                    "description": {"type": "text"},
                    "location": {
                        "type": "geo_point",
                    },
                    "services": {
                        "type": "nested",
                        "properties": {
                            "name": {"type": "text"},
                            "is_paid": {"type": "boolean"},
                        }
                    },
                    "Availability": {"type": "nested", "properties": {"Monday": {"type": "object", "properties": {
                        "start_time": {"type": "date", "format": "HH:mm:ss"},
                        "end_time": {"type": "date", "format": "HH:mm:ss"}}},
                                                                      "Tuesday": {"type": "object", "properties": {
                                                                          "start_time": {"type": "date",
                                                                                         "format": "HH:mm:ss"},
                                                                          "end_time": {"type": "date",
                                                                                       "format": "HH:mm:ss"}}},
                                                                      "Wednesday": {"type": "object", "properties": {
                                                                          "start_time": {"type": "date",
                                                                                         "format": "HH:mm:ss"},
                                                                          "end_time": {"type": "date",
                                                                                       "format": "HH:mm:ss"}}},
                                                                      "Thursday": {"type": "object", "properties": {
                                                                          "start_time": {"type": "date",
                                                                                         "format": "HH:mm:ss"},
                                                                          "end_time": {"type": "date",
                                                                                       "format": "HH:mm:ss"}}},
                                                                      "Friday": {"type": "object", "properties": {
                                                                          "start_time": {"type": "date",
                                                                                         "format": "HH:mm:ss"},
                                                                          "end_time": {"type": "date",
                                                                                       "format": "HH:mm:ss"}}},
                                                                      "Saturday": {"type": "object", "properties": {
                                                                          "start_time": {"type": "date",
                                                                                         "format": "HH:mm:ss"},
                                                                          "end_time": {"type": "date",
                                                                                       "format": "HH:mm:ss"}}},
                                                                      "Sunday": {"type": "object", "properties": {
                                                                          "start_time": {"type": "date",
                                                                                         "format": "HH:mm:ss"},
                                                                          "end_time": {"type": "date",
                                                                                       "format": "HH:mm:ss"}}}}},
                    "holidays": {
                        "type": "nested",
                        "properties": {
                            "name": {"type": "text"},
                            "type": {"type": "text"},
                            "date": {"type": "date"},  # , "format": "d/M/yyyy"
                        }
                    }
                }
            },
            "settings": {
                "index": {
                    "store": {
                        "preload": ["*"]
                    },
                    "mapping": {
                        "total_fields": {
                            "limit": "99999999"
                        }
                    },
                    "auto_expand_replicas": "0-1",
                    "analysis": {
                        "filter": {
                            "front_ngram": {
                                "type": "edge_ngram",
                                "min_gram": "1",
                                "max_gram": "12"
                            },
                            "bigram_joiner": {
                                "max_shingle_size": "2",
                                "token_separator": "",
                                "output_unigrams": "false",
                                "type": "shingle"
                            },
                            "bigram_max_size": {
                                "type": "length",
                                "max": "16",
                                "min": "0"
                            },
                            "phrase_shingle": {
                                "max_shingle_size": "3",
                                "min_shingle_size": "2",
                                "output_unigrams": "true",
                                "type": "shingle"
                            },
                            "en-stem-filter": {
                                "name": "light_english",
                                "type": "stemmer"
                            },
                            "delimiter": {
                                "split_on_numerics": "true",
                                "generate_word_parts": "true",
                                "preserve_original": "false",
                                "catenate_words": "true",
                                "generate_number_parts": "true",
                                "catenate_all": "true",
                                "split_on_case_change": "true",
                                "type": "word_delimiter_graph",
                                "catenate_numbers": "true",
                                "stem_english_possessive": "true"
                            },
                            "en-stop-words-filter": {
                                "type": "stop",
                                "stopwords": "_english_"
                            }
                        },
                        "analyzer": {
                            "i_prefix": {
                                "filter": [
                                    "cjk_width",
                                    "lowercase",
                                    "asciifolding",
                                    "front_ngram"
                                ],
                                "tokenizer": "standard"
                            },
                            "iq_intragram": {
                                "filter": [
                                    "cjk_width",
                                    "lowercase",
                                    "asciifolding"
                                ],
                                "tokenizer": "intragram_tokenizer"
                            },
                            "iq_phrase_shingle": {
                                "filter": [
                                    "cjk_width",
                                    "lowercase",
                                    "asciifolding",
                                    "phrase_shingle"
                                ],
                                "tokenizer": "standard"
                            },
                            "iq_text_delimiter": {
                                "filter": [
                                    "delimiter",
                                    "cjk_width",
                                    "lowercase",
                                    "asciifolding",
                                    "en-stop-words-filter",
                                    "en-stem-filter"
                                ],
                                "tokenizer": "whitespace"
                            },
                            "q_prefix": {
                                "filter": [
                                    "cjk_width",
                                    "lowercase",
                                    "asciifolding"
                                ],
                                "tokenizer": "standard"
                            },
                            "iq_text_base": {
                                "filter": [
                                    "cjk_width",
                                    "lowercase",
                                    "asciifolding",
                                    "en-stop-words-filter"
                                ],
                                "tokenizer": "standard"
                            },
                            "iq_text_stem": {
                                "filter": [
                                    "cjk_width",
                                    "lowercase",
                                    "asciifolding",
                                    "en-stop-words-filter",
                                    "en-stem-filter"
                                ],
                                "tokenizer": "standard"
                            },
                            "iq_text_bigram": {
                                "filter": [
                                    "cjk_width",
                                    "lowercase",
                                    "asciifolding",
                                    "en-stem-filter",
                                    "bigram_joiner",
                                    "bigram_max_size"
                                ],
                                "tokenizer": "standard"
                            }
                        },
                        "tokenizer": {
                            "intragram_tokenizer": {
                                "token_chars": [
                                    "letter",
                                    "digit"
                                ],
                                "min_gram": "3",
                                "type": "ngram",
                                "max_gram": "4"
                            }
                        }
                    },
                    "number_of_replicas": "0",
                    "number_of_shards": "1",
                    "similarity": {
                        "default": {
                            "type": "BM25"
                        }
                    }
                }
            }
        }
        index_settings["mappings"]["properties"].update(string_mappings)

        try:
            self.elastic.indices.create(name, index_settings)
            print("Index Creation Successful.")
        except Exception as exception:
            print("Error Creating new Index.")
            print(exception.__str__())

    def handle(self, index_name=""):
        """
        index_name = "pos_stores_{}".format(datetime.datetime.now().strftime("%d%m%y_%H%M%S"))
        """
        index_name = self.get_index_name(name=index_name, store=True)
        self.remove_indexes(start_pattern="pos_stores")
        self.get_or_create_index(index_name)
        self.start_bulk_indexing(index_name)
        print("Index Populated with records.")
        alias = 'pos_stores'
        if index_name != alias:
            self.generate_alias(index_name, alias)
        self.elastic.indices.refresh(index=index_name)
        self.elastic.search(index=index_name)
        print("Tested Search on alias.")


def store_reindex_elastic() -> bool:
    IndexStore().handle()
    return True