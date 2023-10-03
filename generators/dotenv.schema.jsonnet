{
  title: 'dotenv schema',
  type: 'object',
  required: ['OPENAI_API_KEY'],
  properties: {
    OPENAI_API_KEY: {
      type: 'string',
      examples: [
        'sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
      ],
    },

    DATASET_DIRECTORY: {
      description: 'place to put data',
      type: 'string',
      default: '.',  // current directory
    }
  },
}

