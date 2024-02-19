from flask import Blueprint,request,render_template,redirect,url_for,session,flash
from ..models.modelos import Producto
from datetime import datetime
from app import db