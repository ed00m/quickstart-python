#!/usr/bin/env python3
"""Firebase Admin SDK ML quickstart example."""

import argparse

import firebase_admin
from firebase_admin import ml


# TODO(user): Configure for your project. (See README.md.)
SERVICE_ACCOUNT_KEY = '/path/to/your/service_account_key.json'
STORAGE_BUCKET = 'your-storage-bucket'

credentials = firebase_admin.credentials.Certificate(SERVICE_ACCOUNT_KEY)
firebase_admin.initialize_app(credentials, options={
    'storageBucket': STORAGE_BUCKET
})


def upload_model(model_file, name, tags=None):
  """Upload a tflite model file to the project and publish it."""
  # Load a tflite file and upload it to Cloud Storage
  print('Uploading to Cloud Storage...')
  model_source = ml.TFLiteGCSModelSource.from_tflite_model_file(model_file)

  # Create the model object
  tflite_format = ml.TFLiteFormat(model_source=model_source)
  model = ml.Model(
      display_name=name,
      model_format=tflite_format)
  if tags is not None:
    model.tags = tags

  # Add the model to your Firebase project and publish it
  new_model = ml.create_model(model)
  ml.publish_model(new_model.model_id)

  print('Model uploaded and published:')
  tags = ', '.join(new_model.tags) if new_model.tags is not None else ''
  print('{:<20}{:<10} {}'.format(new_model.display_name, new_model.model_id,
                                 tags))


def list_models(filter_exp=''):
  """List the models in the project."""
  models = ml.list_models(list_filter=filter_exp).iterate_all()
  for model in models:
    tags = ', '.join(model.tags) if model.tags is not None else ''
    print('{:<20}{:<10} {}'.format(model.display_name, model.model_id, tags))


def update_model(model_id, model_file=None, name=None,
                 new_tags=None, remove_tags=None):
  """Update one of the project's models."""
  model = ml.get_model(model_id)

  if model_file is not None:
    # Load a tflite file and upload it to Cloud Storage
    print('Uploading to Cloud Storage...')
    model_source = ml.TFLiteGCSModelSource.from_tflite_model_file(model_file)
    tflite_format = ml.TFLiteFormat(model_source=model_source)
    model.model_format = tflite_format

  if name is not None:
    model.display_name = name

  if new_tags is not None:
    model.tags = new_tags if model.tags is None else model.tags + new_tags

  if remove_tags is not None and model.tags is not None:
    model.tags = list(set(model.tags).difference(set(remove_tags)))

  updated_model = ml.update_model(model)
  ml.publish_model(updated_model.model_id)


def delete_model(model_id):
  """Delete a model from the project."""
  ml.delete_model(model_id)


# The rest of the file just parses the command line and dispatches one of the
# functions above.


def main():
  main_parser = argparse.ArgumentParser()
  subparsers = main_parser.add_subparsers(
      dest='command', required=True, metavar='command')

  new_parser = subparsers.add_parser(
      'new', help='upload a tflite model to your project')
  new_parser.add_argument(
      'model_file', type=str, help='path to the tflite file')
  new_parser.add_argument(
      'name', type=str, help='display name for the new model')
  new_parser.add_argument(
      '-t', '--tags', type=str, help='comma-separated list of tags')

  list_parser = subparsers.add_parser(
      'list', help='list your project\'s models')
  list_parser.add_argument(
      '-f', '--filter', type=str, default='',
      help='''filter expression to limit results (see:
              https://firebase.google.com/docs/ml-kit/manage-hosted-models#list_your_projects_models)''')

  update_parser = subparsers.add_parser(
      'update', help='update one of your project\'s models')
  update_parser.add_argument(
      'model_id', type=valid_id, help='the ID of the model you want to update')
  update_parser.add_argument(
      '-m', '--model_file', type=str, help='path to a new tflite file')
  update_parser.add_argument(
      '-n', '--name', type=str, help='display name for the model')
  update_parser.add_argument(
      '-t', '--new_tags', type=str,
      help='comma-separated list of tags to add')
  update_parser.add_argument(
      '-d', '--remove_tags', type=str,
      help='comma-separated list of tags to remove')

  delete_parser = subparsers.add_parser(
      'delete', help='delete a model from your project')
  delete_parser.add_argument(
      'model_id', type=valid_id, help='the ID of the model you want to delete')

  args = main_parser.parse_args()
  try:
    if args.command == 'new':
      tags = args.tags.split(',') if args.tags is not None else None
      upload_model(args.model_file, args.name, tags)
    elif args.command == 'list':
      list_models(args.filter)
    elif args.command == 'update':
      new_tags = args.new_tags.split(',') if args.new_tags is not None else None
      remove_tags = (
          args.remove_tags.split(',') if args.remove_tags is not None else None)
      update_model(args.model_id, args.model_file, args.name,
                   new_tags, remove_tags)
    elif args.command == 'delete':
      delete_model(args.model_id)
  except firebase_admin.exceptions.NotFoundError:
    print('ERROR: Model not found. Make sure you\'re specifying a valid'
          ' numerical model ID.')


def valid_id(model_id):
  try:
    val = int(model_id)
    return str(val)
  except ValueError:
    raise argparse.ArgumentTypeError('must be a numerical model ID.')


if __name__ == '__main__':
  main()
