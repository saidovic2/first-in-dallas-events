FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application
COPY . .

# Build Next.js app for production
RUN npm run build

# Expose port (Railway will use $PORT)
EXPOSE 3000

# Start production server
CMD ["npm", "run", "start"]
