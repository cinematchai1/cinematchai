FROM node:18-alpine

WORKDIR /app

# Copy dependency files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application source code
COPY . .

# Expose port (default in server.js)
EXPOSE 80

# Start the Node.js server
CMD ["node", "server.js"]
