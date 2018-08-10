import time
import re
import sys
import serial
from serial import Serial
import RPi.GPIO as GPIO
from flask import jsonify

from flask import current_app as app
from flask import (
  Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

bp = Blueprint('rfid', __name__)


@bp.route('/')
def index():
  return render_template('rfid/index.html')


@bp.route('/cards-status', methods=('GET', 'POST'))
@login_required
def card_status():
  if app.RFID_reader.cardInRange():
    app.RFID_reader.resetCardStatus()
    data = app.RFID_reader.readBlock(0, 2)
    return jsonify(status=True, data=data)
  else:
    return jsonify(status=False)


@bp.route('/<int:startblock>/<int:number>/get_data', methods=('GET', 'POST'))
@login_required
def get_data(startblock, number):
  data = app.RFID_reader.readBlock(startblock, number)
  return jsonify(data=data)
  

@bp.route('/<int:t>/<int:b>/<int:d>/<int:m>/<int:y1>/<int:y2>/save', methods=('POST',))
@login_required
def delete(t, b, d, m, y1, y2):
  app.RFID_reader.writeBlock(0, 0, 0, t, b)
  app.RFID_reader.writeBlock(1, d, m, y1, y2)
  return jsonify(data='success')

