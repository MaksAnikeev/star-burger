FROM node:16.14.0 AS parcel
WORKDIR /app
COPY ["package.json", "package-lock.json*", "./"]
RUN npm ci --dev
COPY ./bundles-src ./bundles-src
COPY ./assets ./assets
RUN ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

FROM python:3
WORKDIR /app
COPY --from=parcel ./app ./
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

