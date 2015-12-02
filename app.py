from flask import Flask, request, after_this_request
import gzip
import functools
import json
import pafy
from ip_info import get_info, OWNERS

app = Flask(__name__)


VERSION = '1.0.4'


def gzipped(f):
    @functools.wraps(f)
    def view_func(*args, **kwargs):
        @after_this_request
        def zipper(response):
            accept_encoding = request.headers.get('Accept-Encoding', '')

            if 'gzip' not in accept_encoding.lower():
                return response

            response.direct_passthrough = False

            if response.status_code < 200 or response.status_code >= 300 or 'Content-Encoding' in response.headers:
                return response

            response.data = gzip.compress(response.data)
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Vary'] = 'Accept-Encoding'
            response.headers['Content-Length'] = len(response.data)

            return response

        return f(*args, **kwargs)

    return view_func


@app.route('/')
@gzipped
def home():
    return "Hello world : " + VERSION


ERROR_NO_ID = json.dumps({
    'statusCode': -1,
    'status': 'FAIL',
    'description': "Please provide youtube video's id",
})

ERROR_EXCEPTION = {
    'statusCode': -2,
    'status': 'FAIL',
    'description': "Load data error",
    'message': ''
}


@app.route('/yt/<youtube_id>')
@gzipped
def youtube_info(youtube_id=None):
    if not youtube_id:
        return ERROR_NO_ID

    url = "https://www.youtube.com/watch?v=" + youtube_id

    try:
        video = pafy.new(url)
        streams = video.streams
        stream_urls = []

        for s in streams:
            stream_urls.append({
                'resolution': s.resolution,
                'extension': s.extension,
                'url': s.url
            })

        best = video.getbest()
        best_url = {
            'resolution': best.resolution,
            'extension': best.extension,
            'url': best.url
        }

        sorted(stream_urls, key=lambda x: int(x['resolution'].split('x')[0]))

        return json.dumps({
            'statusCode': 0,
            'status': 'OK',
            'urls': stream_urls,
            'best': best_url
        })
    except Exception as e:
        error = ERROR_EXCEPTION.copy()
        error['message'] = str(e)
        return json.dumps(error)

@app.route('/ip/<ip>')
@gzipped
def get_specified_ip_info(ip):
    info = get_info(ip)
    info['ip'] = ip
    return json.dumps(info)

@app.route('/ip')
@gzipped
def get_ip_info():
    ip = request.remote_addr
    info = get_info(ip)
    info['ip'] = ip

    return json.dumps(info)

@app.route('/ip/owners')
@gzipped
def get_all_owners():
    return json.dumps(OWNERS)


if __name__ == '__main__':
    import os

    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
