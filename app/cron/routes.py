# app/cron/routes.py
import os
from flask import request, jsonify
from extensions import csrf
from . import cron_bp


@cron_bp.route('/weekly-digest')
def weekly_digest():
    """Protected endpoint triggered by external cron services."""
    secret = request.args.get('secret') or request.headers.get('X-Cron-Secret')
    expected = os.getenv('CRON_SECRET')

    if not expected or secret != expected:
        return jsonify({'error': 'unauthorized'}), 401

    from app.utils.weekly_digest import generate_and_send_digests
    count = generate_and_send_digests()

    return jsonify({'status': 'ok', 'sent': count})