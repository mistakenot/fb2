import facebook
import os

token = os.environ['FACEBOOK_TOKEN']
graph = facebook.GraphAPI(access_token=token, version="3.1")
me = graph.get_object(id='me', fields='id')
id = me['id']

print('Using user id {}.'.format(id))

def get_cursor_url(user_id, next_cursor=None):
    if next_cursor == None:
        return '{}/photos?type=tagged&limit=25'.format(id) 
    else:
        return '{}/photos?type=tagged&limit=25&after={}'.format(id, next_cursor)

def download_image(id):
    photo = graph.get_object(id='{}'.format(id), fields='images')
    sorted_images = sorted(photo['images'], key=lambda value: -1 * value['height']) 


images_page = graph.get_object(id='{}/photos?type=tagged'.format(id))
data_block = images_page['data']
next_page = images_page['paging']['cursors']['after']

print('Next page id: {}'.format(next_page))

next_page_all = graph.get_object(id='{}/photos?type=tagged&before={}'.format(id, next_page))
print(next_page_all)