import os

mod_name = 'paper'
spider_cache_dirname = 'spider_cache'
spider_cache_expire = 3600

def get_spider_cache_folder(app):
    return os.path.join(app.instance_path, spider_cache_dirname)