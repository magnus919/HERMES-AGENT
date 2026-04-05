#!/usr/bin/env python3
import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path
from urllib import error, parse, request

HERMES_ENV = Path.home() / '.hermes' / '.env'
DEFAULT_BASE_URL = 'https://api.repliz.com'
DEFAULT_THREADS_GRAPH_BASE_URL = 'https://graph.threads.net'

DEFAULT_THREADS_PROFILE_FIELDS = 'id,username,name,threads_profile_picture_url,threads_biography'
DEFAULT_THREADS_POST_FIELDS = 'id,media_product_type,media_type,permalink,text,timestamp,username,shortcode,is_quote_post,has_replies,reply_audience'


def _load_env_file() -> dict:
    values = {}
    if not HERMES_ENV.exists():
        return values
    for raw_line in HERMES_ENV.read_text(encoding='utf-8', errors='ignore').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        values[key.strip()] = value.strip()
    return values


def _get_setting(name: str, default: str | None = None) -> str | None:
    file_env = _load_env_file()
    return os.environ.get(name) or file_env.get(name) or default


def _require_credentials() -> tuple[str, str, str]:
    access = _get_setting('REPLIZ_ACCESS_KEY')
    secret = _get_setting('REPLIZ_SECRET_KEY')
    base_url = (_get_setting('REPLIZ_BASE_URL', DEFAULT_BASE_URL) or DEFAULT_BASE_URL).rstrip('/')
    missing = [name for name, value in [
        ('REPLIZ_ACCESS_KEY', access),
        ('REPLIZ_SECRET_KEY', secret),
    ] if not value]
    if missing:
        print(json.dumps({'error': 'missing_credentials', 'missing': missing}), file=sys.stderr)
        raise SystemExit(2)
    return access, secret, base_url


def _auth_header(access: str, secret: str) -> str:
    token = base64.b64encode(f'{access}:{secret}'.encode('utf-8')).decode('ascii')
    return f'Basic {token}'


def _parse_response_text(text: str):
    text = text.strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {'raw': text}


def _request(method: str, path: str, *, query: dict | None = None, payload: dict | list | None = None):
    access, secret, base_url = _require_credentials()
    url = base_url + path
    if query:
        filtered = {k: v for k, v in query.items() if v is not None}
        if filtered:
            url += '?' + parse.urlencode(filtered, doseq=True)
    headers = {
        'Accept': 'application/json',
        'Authorization': _auth_header(access, secret),
    }
    body = None
    if payload is not None:
        headers['Content-Type'] = 'application/json'
        body = json.dumps(payload).encode('utf-8')
    req = request.Request(url, data=body, headers=headers, method=method.upper())
    try:
        with request.urlopen(req, timeout=60) as resp:
            text = resp.read().decode('utf-8', errors='replace')
            return resp.status, _parse_response_text(text)
    except error.HTTPError as exc:
        text = exc.read().decode('utf-8', errors='replace')
        return exc.code, _parse_response_text(text)


def _redact_secrets(value):
    if isinstance(value, dict):
        redacted = {}
        for key, item in value.items():
            if key == 'token' and isinstance(item, dict):
                redacted[key] = {subkey: '[REDACTED]' if item.get(subkey) else item.get(subkey) for subkey in item}
            elif key in {'access_token', 'refresh_token'}:
                redacted[key] = '[REDACTED]' if item else item
            else:
                redacted[key] = _redact_secrets(item)
        return redacted
    if isinstance(value, list):
        return [_redact_secrets(item) for item in value]
    if isinstance(value, str):
        value = re.sub(r'(access_token=)[^&\s]+', r'\1[REDACTED]', value)
        value = re.sub(r'([?&]token=)[^&\s]+', r'\1[REDACTED]', value)
    return value


def _emit(status: int, payload, compact: bool = False):
    result = {'status': status, 'data': _redact_secrets(payload)}
    if compact:
        print(json.dumps(result, separators=(',', ':'), ensure_ascii=False))
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    if status >= 400:
        raise SystemExit(1)


def _read_json_payload(args) -> dict | list:
    sources = [bool(args.file), bool(args.data), bool(args.stdin)]
    if sum(sources) != 1:
        print(json.dumps({'error': 'exactly_one_input_required', 'accepted': ['--file', '--data', '--stdin']}), file=sys.stderr)
        raise SystemExit(2)
    if args.file:
        raw = Path(args.file).read_text(encoding='utf-8')
    elif args.data:
        raw = args.data
    else:
        raw = sys.stdin.read()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        print(json.dumps({'error': 'invalid_json', 'message': str(exc)}), file=sys.stderr)
        raise SystemExit(2)


def cmd_account_list(args):
    status, payload = _request('GET', '/public/account', query={
        'page': args.page,
        'limit': args.limit,
        'search': args.search,
    })
    _emit(status, payload, args.compact)


def cmd_account_get(args):
    status, payload = _request('GET', f'/public/account/{args.id}')
    _emit(status, payload, args.compact)


def cmd_schedule_list(args):
    status, payload = _request('GET', '/public/schedule', query={
        'page': args.page,
        'limit': args.limit,
        'search': args.search,
    })
    _emit(status, payload, args.compact)


def cmd_schedule_get(args):
    status, payload = _request('GET', f'/public/schedule/{args.id}')
    _emit(status, payload, args.compact)


def cmd_schedule_create(args):
    payload = _read_json_payload(args)
    status, response = _request('POST', '/public/schedule', payload=payload)
    _emit(status, response, args.compact)


def cmd_schedule_delete(args):
    status, payload = _request('DELETE', f'/public/schedule/{args.id}')
    _emit(status, payload, args.compact)


def cmd_queue_list(args):
    status, payload = _request('GET', '/public/queue', query={
        'page': args.page,
        'limit': args.limit,
        'search': args.search,
    })
    _emit(status, payload, args.compact)


def cmd_queue_get(args):
    status, payload = _request('GET', f'/public/queue/{args.id}')
    _emit(status, payload, args.compact)


def cmd_queue_reply(args):
    status, payload = _request('POST', f'/public/queue/{args.id}', payload={'text': args.text})
    _emit(status, payload, args.compact)


def _threads_graph_base_url() -> str:
    return (_get_setting('THREADS_GRAPH_BASE_URL', DEFAULT_THREADS_GRAPH_BASE_URL) or DEFAULT_THREADS_GRAPH_BASE_URL).rstrip('/')


def _require_threads_account(account_id: str, compact: bool = False):
    status, payload = _request('GET', f'/public/account/{account_id}')
    if status >= 400:
        _emit(status, payload, compact)

    account_type = payload.get('type')
    if account_type != 'threads':
        _emit(400, {
            'error': 'account_not_threads',
            'account_id': account_id,
            'type': account_type,
        }, compact)

    token = ((payload.get('token') or {}).get('access') or '').strip()
    if not token:
        _emit(400, {
            'error': 'missing_threads_access_token',
            'account_id': account_id,
        }, compact)

    account_summary = {
        'id': payload.get('id') or payload.get('_id') or account_id,
        'generatedId': payload.get('generatedId'),
        'name': payload.get('name'),
        'username': payload.get('username'),
        'type': payload.get('type'),
        'isConnected': payload.get('isConnected'),
    }
    return account_summary, token


def _threads_request(path: str, token: str, *, query: dict | None = None):
    base_url = _threads_graph_base_url()
    url = base_url + path
    params = {k: v for k, v in (query or {}).items() if v is not None}
    params['access_token'] = token
    url += '?' + parse.urlencode(params, doseq=True)

    req = request.Request(url, headers={
        'Accept': 'application/json',
        'User-Agent': 'Hermes',
    }, method='GET')
    try:
        with request.urlopen(req, timeout=60) as resp:
            text = resp.read().decode('utf-8', errors='replace')
            return resp.status, _parse_response_text(text)
    except error.HTTPError as exc:
        text = exc.read().decode('utf-8', errors='replace')
        return exc.code, _parse_response_text(text)


def cmd_threads_profile(args):
    account, token = _require_threads_account(args.account_id, args.compact)
    status, payload = _threads_request('/v1.0/me', token, query={
        'fields': args.fields,
    })
    _emit(status, {
        'account': account,
        'profile': payload,
    }, args.compact)


def cmd_threads_posts(args):
    account, token = _require_threads_account(args.account_id, args.compact)
    status, payload = _threads_request('/v1.0/me/threads', token, query={
        'fields': args.fields,
        'limit': args.limit,
        'since': args.since,
        'until': args.until,
        'after': args.after,
        'before': args.before,
    })
    _emit(status, {
        'account': account,
        'posts': payload,
    }, args.compact)


def cmd_threads_post_get(args):
    account, token = _require_threads_account(args.account_id, args.compact)
    status, payload = _threads_request(f'/v1.0/{args.post_id}', token, query={
        'fields': args.fields,
    })
    _emit(status, {
        'account': account,
        'post': payload,
    }, args.compact)


def _add_compact_flag(subparser):
    subparser.add_argument('--compact', action='store_true', help='Print compact JSON')
    return subparser


def build_parser():
    parser = argparse.ArgumentParser(description='Repliz Public API helper')
    top = parser.add_subparsers(dest='resource', required=True)

    account = top.add_parser('account', help='Account operations')
    account_sub = account.add_subparsers(dest='action', required=True)
    account_list = _add_compact_flag(account_sub.add_parser('list', help='List accounts'))
    account_list.add_argument('--page', type=int, default=1)
    account_list.add_argument('--limit', type=int, default=10)
    account_list.add_argument('--search')
    account_list.set_defaults(func=cmd_account_list)
    account_get = _add_compact_flag(account_sub.add_parser('get', help='Get one account'))
    account_get.add_argument('id')
    account_get.set_defaults(func=cmd_account_get)

    schedule = top.add_parser('schedule', help='Schedule operations')
    schedule_sub = schedule.add_subparsers(dest='action', required=True)
    schedule_list = _add_compact_flag(schedule_sub.add_parser('list', help='List schedules'))
    schedule_list.add_argument('--page', type=int, default=1)
    schedule_list.add_argument('--limit', type=int, default=10)
    schedule_list.add_argument('--search')
    schedule_list.set_defaults(func=cmd_schedule_list)
    schedule_get = _add_compact_flag(schedule_sub.add_parser('get', help='Get one schedule'))
    schedule_get.add_argument('id')
    schedule_get.set_defaults(func=cmd_schedule_get)
    schedule_create = _add_compact_flag(schedule_sub.add_parser('create', help='Create schedule from JSON payload'))
    group = schedule_create.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', help='Path to JSON payload')
    group.add_argument('--data', help='Inline JSON payload')
    group.add_argument('--stdin', action='store_true', help='Read JSON payload from stdin')
    schedule_create.set_defaults(func=cmd_schedule_create)
    schedule_delete = _add_compact_flag(schedule_sub.add_parser('delete', help='Delete schedule by id'))
    schedule_delete.add_argument('id')
    schedule_delete.set_defaults(func=cmd_schedule_delete)

    queue = top.add_parser('queue', help='Queue operations')
    queue_sub = queue.add_subparsers(dest='action', required=True)
    queue_list = _add_compact_flag(queue_sub.add_parser('list', help='List queue items'))
    queue_list.add_argument('--page', type=int, default=1)
    queue_list.add_argument('--limit', type=int, default=10)
    queue_list.add_argument('--search')
    queue_list.set_defaults(func=cmd_queue_list)
    queue_get = _add_compact_flag(queue_sub.add_parser('get', help='Get one queue item'))
    queue_get.add_argument('id')
    queue_get.set_defaults(func=cmd_queue_get)
    queue_reply = _add_compact_flag(queue_sub.add_parser('reply', help='Reply to queue comment'))
    queue_reply.add_argument('id')
    queue_reply.add_argument('--text', required=True)
    queue_reply.set_defaults(func=cmd_queue_reply)

    threads = top.add_parser('threads', help='Read Threads account data via the Threads Graph API using the token stored in Repliz')
    threads_sub = threads.add_subparsers(dest='action', required=True)

    threads_profile = _add_compact_flag(threads_sub.add_parser('profile', help='Get Threads profile for a connected Repliz account'))
    threads_profile.add_argument('account_id', help='Repliz account id for a connected Threads account')
    threads_profile.add_argument('--fields', default=DEFAULT_THREADS_PROFILE_FIELDS, help='Comma-separated Threads profile fields')
    threads_profile.set_defaults(func=cmd_threads_profile)

    threads_posts = _add_compact_flag(threads_sub.add_parser('posts', help='List Threads posts for a connected Repliz account'))
    threads_posts.add_argument('account_id', help='Repliz account id for a connected Threads account')
    threads_posts.add_argument('--limit', type=int, default=10)
    threads_posts.add_argument('--since', help='Optional lower timestamp bound accepted by the Threads Graph API')
    threads_posts.add_argument('--until', help='Optional upper timestamp bound accepted by the Threads Graph API')
    threads_posts.add_argument('--after', help='Pagination cursor for the next page')
    threads_posts.add_argument('--before', help='Pagination cursor for the previous page')
    threads_posts.add_argument('--fields', default=DEFAULT_THREADS_POST_FIELDS, help='Comma-separated Threads post fields')
    threads_posts.set_defaults(func=cmd_threads_posts)

    threads_post = _add_compact_flag(threads_sub.add_parser('post', help='Get one Threads post by post id for a connected Repliz account'))
    threads_post.add_argument('account_id', help='Repliz account id for a connected Threads account')
    threads_post.add_argument('post_id', help='Threads post id as returned by threads posts')
    threads_post.add_argument('--fields', default=DEFAULT_THREADS_POST_FIELDS, help='Comma-separated Threads post fields')
    threads_post.set_defaults(func=cmd_threads_post_get)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
