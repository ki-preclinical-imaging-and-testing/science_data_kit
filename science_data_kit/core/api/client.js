/**
 * JavaScript Client Library for Science Data Kit API
 *
 * This module provides a JavaScript client library for interacting with the Science Data Kit API,
 * making it easy to integrate the SDK's functionality into web applications and Node.js applications.
 */

/**
 * Exception class for API client errors.
 */
class APIClientError extends Error {
  /**
   * Initialize the API client error.
   * 
   * @param {string} message - The error message.
   * @param {number} [statusCode=null] - The HTTP status code.
   * @param {Object} [response=null] - The response from the API.
   */
  constructor(message, statusCode = null, response = null) {
    super(message);
    this.name = 'APIClientError';
    this.statusCode = statusCode;
    this.response = response;
  }
}

/**
 * Client for interacting with the Science Data Kit API.
 */
class APIClient {
  /**
   * Initialize the API client.
   * 
   * @param {string} baseUrl - The base URL of the API.
   * @param {number} [timeout=30000] - The timeout for API requests in milliseconds.
   */
  constructor(baseUrl, timeout = 30000) {
    this.baseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
    this.timeout = timeout;
    this.token = null;
  }

  /**
   * Make a full URL from a path.
   * 
   * @param {string} path - The path to append to the base URL.
   * @returns {string} The full URL.
   * @private
   */
  _makeUrl(path) {
    const trimmedPath = path.startsWith('/') ? path.slice(1) : path;
    return `${this.baseUrl}/${trimmedPath}`;
  }

  /**
   * Get the headers for API requests.
   * 
   * @returns {Object} The headers.
   * @private
   */
  _getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  /**
   * Handle an API response.
   * 
   * @param {Response} response - The response from the API.
   * @returns {Promise<Object>} The parsed response data.
   * @throws {APIClientError} If the response indicates an error.
   * @private
   */
  async _handleResponse(response) {
    let data;
    try {
      data = await response.json();
    } catch (error) {
      throw new APIClientError(
        `Invalid JSON response: ${await response.text()}`,
        response.status
      );
    }

    if (!response.ok) {
      let errorMessage = 'Unknown error';
      if (data.error && data.error.message) {
        errorMessage = data.error.message;
      }

      throw new APIClientError(
        errorMessage,
        response.status,
        data
      );
    }

    return data;
  }

  /**
   * Make an API request.
   * 
   * @param {string} method - The HTTP method (GET, POST, PUT, DELETE, etc.).
   * @param {string} path - The request path.
   * @param {Object} [params=null] - The query parameters.
   * @param {Object} [data=null] - The request body.
   * @returns {Promise<Object>} The parsed response data.
   * @throws {APIClientError} If the request fails.
   * @private
   */
  async _request(method, path, params = null, data = null) {
    let url = this._makeUrl(path);
    const headers = this._getHeaders();
    const options = {
      method,
      headers,
      timeout: this.timeout
    };

    // Add query parameters to URL if provided
    if (params) {
      const queryParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        queryParams.append(key, value);
      });
      url += `?${queryParams.toString()}`;
    }

    // Add request body if provided
    if (data) {
      options.body = JSON.stringify(data);
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);
      options.signal = controller.signal;

      const response = await fetch(url, options);
      clearTimeout(timeoutId);

      return await this._handleResponse(response);
    } catch (error) {
      if (error.name === 'AbortError') {
        throw new APIClientError(`Request timed out after ${this.timeout}ms`);
      }
      throw new APIClientError(`Request failed: ${error.message}`);
    }
  }

  /**
   * Log in to the API.
   * 
   * @param {string} userId - The user ID to log in with.
   * @returns {Promise<Object>} The login response data.
   */
  async login(userId) {
    const response = await this._request(
      'POST',
      '/api/session/login',
      null,
      { user_id: userId }
    );

    if (response.token) {
      this.token = response.token;
    }

    return response;
  }

  /**
   * Log out from the API.
   * 
   * @returns {Promise<Object>} The logout response data.
   */
  async logout() {
    if (!this.token) {
      return { message: 'Not logged in' };
    }

    const response = await this._request(
      'DELETE',
      '/api/session/logout'
    );

    this.token = null;

    return response;
  }

  /**
   * Get session information.
   * 
   * @returns {Promise<Object>} The session information.
   */
  async getSession() {
    return await this._request(
      'GET',
      '/api/session'
    );
  }

  /**
   * Create a new session.
   * 
   * @param {Object} data - The session data.
   * @returns {Promise<Object>} The created session data.
   */
  async createSession(data) {
    return await this._request(
      'POST',
      '/api/session',
      null,
      data
    );
  }

  /**
   * Update a session.
   * 
   * @param {Object} data - The updated session data.
   * @returns {Promise<Object>} The updated session data.
   */
  async updateSession(data) {
    return await this._request(
      'PUT',
      '/api/session',
      null,
      data
    );
  }

  /**
   * Delete a session.
   * 
   * @returns {Promise<Object>} The response data.
   */
  async deleteSession() {
    return await this._request(
      'DELETE',
      '/api/session'
    );
  }

  /**
   * Get database information.
   * 
   * @returns {Promise<Object>} The database information.
   */
  async getDatabaseInfo() {
    return await this._request(
      'GET',
      '/api/database'
    );
  }

  /**
   * Execute a database query.
   * 
   * @param {string} query - The query to execute.
   * @param {Object} [params=null] - The query parameters.
   * @returns {Promise<Object>} The query results.
   */
  async executeQuery(query, params = null) {
    const data = { query };
    if (params) {
      data.params = params;
    }

    return await this._request(
      'POST',
      '/api/database/query',
      null,
      data
    );
  }

  /**
   * Create a new database.
   * 
   * @param {Object} data - The database data.
   * @returns {Promise<Object>} The created database data.
   */
  async createDatabase(data) {
    return await this._request(
      'POST',
      '/api/database',
      null,
      data
    );
  }

  /**
   * Update a database.
   * 
   * @param {Object} data - The updated database data.
   * @returns {Promise<Object>} The updated database data.
   */
  async updateDatabase(data) {
    return await this._request(
      'PUT',
      '/api/database',
      null,
      data
    );
  }

  /**
   * Delete a database.
   * 
   * @returns {Promise<Object>} The response data.
   */
  async deleteDatabase() {
    return await this._request(
      'DELETE',
      '/api/database'
    );
  }
}

/**
 * High-level client for the Science Data Kit API.
 * 
 * This class provides a more user-friendly interface for common SDK operations.
 */
class SDKClient {
  /**
   * Initialize the SDK client.
   * 
   * @param {string} baseUrl - The base URL of the API.
   * @param {string} [userId=null] - The user ID to log in with. If provided, the client will automatically log in.
   */
  constructor(baseUrl, userId = null) {
    this.apiClient = new APIClient(baseUrl);

    if (userId) {
      this.login(userId);
    }
  }

  /**
   * Log in to the SDK.
   * 
   * @param {string} userId - The user ID to log in with.
   * @returns {Promise<Object>} The login response data.
   */
  async login(userId) {
    return await this.apiClient.login(userId);
  }

  /**
   * Log out from the SDK.
   * 
   * @returns {Promise<Object>} The logout response data.
   */
  async logout() {
    return await this.apiClient.logout();
  }

  /**
   * Get information about the current user.
   * 
   * @returns {Promise<Object>} The user information.
   */
  async getUserInfo() {
    return await this.apiClient.getSession();
  }

  /**
   * Execute a database query and return the results.
   * 
   * @param {string} query - The query to execute.
   * @param {Object} [params=null] - The query parameters.
   * @returns {Promise<Array>} The query results.
   */
  async query(query, params = null) {
    const response = await this.apiClient.executeQuery(query, params);
    return response.results || [];
  }

  /**
   * Create a new session with a database.
   * 
   * @param {string} sessionName - The name of the session.
   * @param {string} databaseName - The name of the database.
   * @returns {Promise<Object>} The created session data.
   */
  async createSessionWithDatabase(sessionName, databaseName) {
    // Create the database
    const databaseResponse = await this.apiClient.createDatabase({
      name: databaseName
    });

    // Create the session with the database
    const sessionResponse = await this.apiClient.createSession({
      name: sessionName,
      database_id: databaseResponse.database_id
    });

    return sessionResponse;
  }
}

// Export the classes for use in both Node.js and browser environments
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    APIClientError,
    APIClient,
    SDKClient
  };
} else {
  // For browser environments
  window.APIClientError = APIClientError;
  window.APIClient = APIClient;
  window.SDKClient = SDKClient;
}
