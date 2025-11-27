import { defineConfig } from '@hey-api/openapi-ts'
import { defaultPlugins } from '@hey-api/openapi-ts'

export default defineConfig({
  input: 'http://localhost:8098/openapi.json',
  output: 'src/schemas',
  plugins: [
    ...defaultPlugins,
    '@hey-api/client-fetch',
    {
      name: '@hey-api/schemas',
      type: 'form',
    },
  ],

})
