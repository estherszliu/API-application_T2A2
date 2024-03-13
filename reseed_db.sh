#!/bin/bash

flask db drop
flask db create
flask db seed