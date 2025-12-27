# Use official Node image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port (default for CRA)
EXPOSE 3000

# Start app
CMD ["npm", "start"]
