from flask_cors import CORS
from flask import Flask, request, Response, json, redirect
from proxyservice import settings
from proxyservice.router import Router
from proxyservice.server.errors import UnauthorizedError

application = Flask(__name__)
CORS(application, resources={r"/*": {"origins": "*"}})

application.config.update(
    SECRET_KEY=settings.SECRET_KEY
)


@application.route('/health', methods=['GET'])
def health_check():
    return Response(status=200)


@application.route('/get', methods=['POST'])
def proxy_get():
    try:

        parameters = request.get_json(force=True)

        if 'solve' in parameters:
            solve = parameters['solve']
        else:
            solve = False

        if 'proxy' in parameters:
            proxy = parameters['proxy']
        else:
            raise UnauthorizedError('No proxy specified')

        if 'url' in parameters:
            url = parameters['url']
        else:
            raise UnauthorizedError('No url specified')

        if 'params' in parameters:
            params = parameters['params']
        else:
            params = None

        if 'timeout' in parameters:
            timeout = parameters['timeout']
        else:
            timeout = None

        if 'headers' in parameters:
            headers = parameters['headers']
        else:
            headers = None

        router = Router(url=url, proxy=proxy,
                        timeout=timeout,
                        headers=headers)

        data = router.fetch_page(params=params)

        if not data['success']:
            status = 401
        else:
            status = 200

        return Response(
            status=status,
            mimetype='application/json',
            response=json.dumps(data)
        )

    except UnauthorizedError as e:
        error = {
            'error': str(e),
            'success': False,
            'type': 'fetch-route'
        }

        return Response(status=403, mimetype='application/json', response=json.dumps(error))

    except Exception as e:

        error = {
            'error': str(e),
            'success': False,
            'type': 'fetch-route'
        }

        return Response(status=500, mimetype='application/json', response=json.dumps(error))


@application.route('/post', methods=['POST'])
def proxy_post():
    try:

        parameters = request.get_json(force=True)

        if 'proxy' in parameters:
            proxy = parameters['proxy']
        else:
            raise UnauthorizedError('No proxy specified')

        if 'url' in parameters:
            url = parameters['url']
        else:
            raise UnauthorizedError('No url specified')

        if 'params' in parameters:
            params = parameters['params']
        else:
            params = None

        if 'timeout' in parameters:
            timeout = parameters['timeout']
        else:
            timeout = None

        if 'headers' in parameters:
            headers = parameters['headers']
        else:
            headers = None

        if 'body' in parameters:
            body = parameters['body']
        else:
            body = None

        router = Router(url=url, proxy=proxy, timeout=timeout,
                        headers=headers, body=body)

        data = router.submit_data(params)

        if not data['success']:
            status = 401
        else:
            status = 200

        return Response(
            status=status,
            mimetype='application/json',
            response=json.dumps(data)
        )

    except UnauthorizedError as e:
        error = {
            'error': str(e),
            'success': False,
            'type': 'post-route'
        }

        return Response(status=403, mimetype='application/json', response=json.dumps(error))

    except Exception as e:

        error = {
            'error': str(e),
            'success': False,
            'type': 'post-route'
        }

        return Response(status=500, mimetype='application/json', response=json.dumps(error))


@application.errorhandler(404)
def handle_page_not_found(e):

    error = {
        'error': str(e),
        'success': False
    }

    return Response(
        status=404,
        mimetype='application/json',
        response=json.dumps(error)
    )
