from pathlib import Path
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components
from kbcstorage.client import Client

frontend_dir = (Path(__file__).parent / "frontend").absolute()

_component_func = components.declare_component(
	"keboola_api", path=str(frontend_dir)
)


def upload(url,key,table_name,bucket_id,file_path,primary_key):
    client = Client(url, key)
    try:
        return client.tables.create(name=table_name,
                            bucket_id=bucket_id,
                            file_path=file_path,
                            primary_key=primary_key) + " successfully created!!"
    except Exception as e:
        return str(e)   

def load(url,key,table_id,file_path,is_incremental=False, delimiter=',',
             enclosure='"', escaped_by='', columns=None,
             without_headers=False):
    client = Client(url, key)
    try:
        _= client.tables.load(table_id=table_id,
                            file_path=file_path,
                            is_incremental=is_incremental, 
                            delimiter=delimiter,
                            enclosure=enclosure, 
                            escaped_by=escaped_by,
                            columns=columns,
                            without_headers=without_headers)
        return f"{table_id} has been successfully loaded!!"
    except Exception as e:
        return str(e)   

def list_buckets(keboola_URL,keboola_key):
    client = Client(keboola_URL, keboola_key)
    try:    
        return client.buckets.list() 
    except Exception as e:
        return str(e)

def list_tables(keboola_URL,keboola_key):
    client = Client(keboola_URL, keboola_key)
    try:
        return client.tables.list()
    except Exception as e:
        return str(e)  

def create_or_update(keboola_URL,
                     keboola_key,
                     table_name,
                     bucket_id,
                     file_path,
                     primary_key,
                     is_incremental=False, 
                     delimiter=',',
                     enclosure='"', 
                     escaped_by='', 
                     columns=None,
                     without_headers=False):
    
    client = Client(keboola_URL, keboola_key)
    # check whether a table in the bucket exists. If so, retrieve its table_id
    try:
        try:
            tables = client.tables.list()

        except Exception as e:
            return str(e)
        # there will be 0 or 1 hit
        table_def = list(filter(lambda x: x['bucket']['id']==bucket_id and x['name']==table_name, tables))
        if table_def:
            table_id = table_def[0]['id']
            # table already exists --> load
            try:
                _= client.tables.load(table_id=table_id,
                                    file_path=file_path,
                                    is_incremental=is_incremental, 
                                    delimiter=delimiter,
                                    enclosure=enclosure, 
                                    escaped_by=escaped_by,
                                    columns=columns,
                                    without_headers=without_headers) 
                return f"{table_name} has been updated."
            except Exception as e:
                return str(e)    
        else:
            # table does not exist --> create
            try:
                return client.tables.create(name=table_name,
                                    bucket_id=bucket_id,
                                    file_path=file_path,
                                    primary_key=primary_key) + " successfully created!!"
            except Exception as e:
                return str(e)   
    except Exception as e:
        return str(e)         


def delete_table(keboola_URL,keboola_key,keboola_table_id):
    client = Client(keboola_URL, keboola_key)
    try:
        ret=client.tables.delete(table_id=keboola_table_id)
        if ret is None:
            ret=keboola_table_id+ " has been succesfully deleted!"
        return ret
    except Exception as e:
        return str(e)  

def delete_bucket(keboola_URL,keboola_key,keboola_bucket_id):
    client = Client(keboola_URL, keboola_key)
    try:
        ret=client.buckets.delete(bucket_id=keboola_bucket_id)
        if ret is None:
            ret=keboola_bucket_id+ " has been succesfully deleted!"
        return ret
    except Exception as e:
        return str(e)  

def keboola_delete_bucket(
    keboola_URL: str,
    keboola_key:str,
    keboola_bucket_id:str,
    key: str,
    api_only:Optional[bool] = False,
    label:Optional[str] = None,
):
    component_value = _component_func(label=label,default="",key=key,api_only=api_only)  
    if st.session_state.get(key) is not None:
        if st.session_state.get('_'+key)!=st.session_state[key]:
            st.session_state['_'+key]=component_value
            if api_only==False:
                with st.spinner("Deleting Bucket..."):
                    ret= delete_bucket(keboola_URL,keboola_key,keboola_bucket_id)
            else:
                ret= delete_bucket(keboola_URL,keboola_key,keboola_bucket_id)       
            st.session_state['__'+key]=ret
            return ret
        return st.session_state['__'+key]
    return ""

def keboola_delete_table(
    keboola_URL: str,
    keboola_key:str,
    keboola_table_id:str,
    key: str,
    api_only:Optional[bool] = False,
    label:Optional[str] = None,
):

    component_value = _component_func(label=label,default="",key=key,api_only=api_only)  
    if st.session_state.get(key) is not None:
        if st.session_state.get('_'+key)!=st.session_state[key]:
            st.session_state['_'+key]=component_value
            if api_only==False:
                with st.spinner("Deleting Table..."):
                    ret= delete_table(keboola_URL,keboola_key,keboola_table_id)
            else:
                ret= delete_table(keboola_URL,keboola_key,keboola_table_id)       
            st.session_state['__'+key]=ret
            return ret
        return st.session_state['__'+key]
    return ""

def keboola_table_list(
    keboola_URL: str,
    keboola_key:str,
    key: str,
    api_only:Optional[bool] = False,
    label:Optional[str] = None,
):
    component_value = _component_func(label=label,default="",key=key,api_only=api_only)  
    if st.session_state.get(key) is not None:
        if st.session_state.get('_'+key)!=st.session_state[key]:
            st.session_state['_'+key]=component_value
            if api_only==False:
                with st.spinner("Getting Tables..."):
                    ret= list_tables(keboola_URL,keboola_key)
            else:
                ret= list_tables(keboola_URL,keboola_key)        
            st.session_state['__'+key]=ret
            return ret
        return st.session_state['__'+key]
    return ""

def keboola_bucket_list(
    keboola_URL: str,
    keboola_key:str,
    key: str,
    api_only:Optional[bool] = False,
    label:Optional[str] = None,
):
    component_value = _component_func(label=label,default="",key=key,api_only=api_only)  
    if st.session_state.get(key) is not None:
        if st.session_state.get('_'+key)!=st.session_state[key]:
            st.session_state['_'+key]=component_value
            if api_only==False:
                with st.spinner("Getting Buckets..."):
                    ret= list_buckets(keboola_URL,keboola_key)
            else:
                ret= list_buckets(keboola_URL,keboola_key)       
            st.session_state['__'+key]=ret
            return ret
        return st.session_state['__'+key]
    return ""

def keboola_upload(
    keboola_URL: str,
    keboola_key:str,
    keboola_table_name:str,
    keboola_bucket_id:str,
    keboola_file_path:str,
    keboola_primary_key:list,
    key: str,
    api_only:Optional[bool] = False,
    label:Optional[str] = None,
):
    component_value = _component_func(label=label,default="",key=key,api_only=api_only)  
    if st.session_state.get(key) is not None:
        if st.session_state.get('_'+key)!=st.session_state[key]:
            st.session_state['_'+key]=component_value
            if api_only==False:
                with st.spinner("Uploading..."):
                    ret= upload(keboola_URL,keboola_key,keboola_table_name,keboola_bucket_id,keboola_file_path,keboola_primary_key)
            else:
                ret= upload(keboola_URL,keboola_key,keboola_table_name,keboola_bucket_id,keboola_file_path,keboola_primary_key)       
            st.session_state['__'+key]=ret
            return ret
        return st.session_state['__'+key]
    return ""

def keboola_create_update(
    keboola_URL: str,
    keboola_key:str,
    keboola_table_name:str,
    keboola_bucket_id:str,
    keboola_file_path:str,
    keboola_primary_key:list,
    key: str,
    keboola_is_incremental = False,
    api_only:Optional[bool] = False,
    label:Optional[str] = None,
):
    component_value = _component_func(label=label,default="",key=key,api_only=api_only)  
    if st.session_state.get(key) is not None:
        if st.session_state.get('_'+key)!=st.session_state[key]:
            st.session_state['_'+key]=component_value
            if api_only==False:
                with st.spinner("Updating..."):
                    ret= create_or_update(keboola_URL,keboola_key,keboola_table_name,keboola_bucket_id,keboola_file_path,keboola_primary_key,keboola_is_incremental)
            else:
                ret= create_or_update(keboola_URL,keboola_key,keboola_table_name,keboola_bucket_id,keboola_file_path,keboola_primary_key,keboola_is_incremental)       
            st.session_state['__'+key]=ret
            return ret
        return st.session_state['__'+key]
    return ""
  
