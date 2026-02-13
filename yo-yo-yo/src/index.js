export class Sandbox {
  constructor(state, env) {
    this.state = state;
    this.env = env;
  }

  async fetch(request) {
    return new Response("Sandbox Durable Object");
  }
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Route to Durable Object if path starts with /sandbox
    if (url.pathname.startsWith("/sandbox")) {
      const id = env.SANDBOX.idFromName("default");
      const stub = env.SANDBOX.get(id);
      return stub.fetch(request);
    }

    // Serve the OpenClaw Admin Dashboard
    const html = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 600px;
            width: 100%;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { color: #333; margin-bottom: 20px; font-size: 2.5em; }
        p { color: #666; margin-bottom: 30px; line-height: 1.6; }
        .btn {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            border-radius: 30px;
            text-decoration: none;
            font-weight: bold;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        .yo-yo {
            font-size: 4em;
            margin-bottom: 20px;
            animation: spin 2s linear infinite;
        }
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="yo-yo">🪀</div>
        <h1>Yo-Yo Dashboard</h1>
        <p>Welcome to the Yo-Yo OpenClaw Dashboard. Click below to access the full OpenClaw Admin interface.</p>
        <a href="https://openclawsandbox.yksanjo.workers.dev/_admin/" class="btn">Open Admin Dashboard</a>
    </div>
</body>
</html>`;

    return new Response(html, {
      headers: { "content-type": "text/html;charset=utf-8" },
    });
  },
};
