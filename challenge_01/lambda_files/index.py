def handler(event, context):
    print("Hello, Pulumi!")
    return {
        'statusCode': 200,
        'body': 'Hello, Pulumi!'
    }