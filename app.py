# ==========================================
# SK 2.0 - COMPLETE FLASK BACKEND
# CHAT + VOICE + MEMORY + PC CONTROL
# ==========================================

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from brain import ask_ai

from memory import (
    get_memories,
    add_memory,
    delete_memory,
    clear_memories
)

import os
import subprocess


# ==========================================
# APP CONFIGURATION
# ==========================================

app = Flask(__name__)

# Allow Frontend to communicate with Backend
CORS(app)


# ==========================================
# FOLDER PATHS
# ==========================================

# This file is:
# SK2.0/Backend/app.py

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# Frontend is:
# SK2.0/Frontend/

FRONTEND_DIR = os.path.abspath(
    os.path.join(
        BASE_DIR,
        "..",
        "Frontend"
    )
)


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    index_file = os.path.join(
        FRONTEND_DIR,
        "index.html"
    )

    if os.path.exists(index_file):

        return send_from_directory(
            FRONTEND_DIR,
            "index.html"
        )

    return jsonify({
        "success": True,
        "app": "SK 2.0",
        "status": "online",
        "message": "Frontend index.html not found."
    })


# ==========================================
# FRONTEND FILES
# ==========================================

@app.route("/<path:filename>")
def frontend_files(filename):

    file_path = os.path.join(
        FRONTEND_DIR,
        filename
    )

    if os.path.exists(file_path):

        return send_from_directory(
            FRONTEND_DIR,
            filename
        )

    return jsonify({
        "success": False,
        "error": "File not found."
    }), 404


# ==========================================
# STATUS
# ==========================================

@app.route(
    "/api/status",
    methods=["GET"]
)
def api_status():

    return jsonify({
        "success": True,
        "status": "online",
        "app": "SK 2.0",
        "assistant": "SK 2.0",
        "version": "2.0",
        "backend": "Flask",
        "chat": True,
        "voice": True,
        "memory": True,
        "pc_control": True
    })


# ==========================================
# HEALTH
# ==========================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def api_health():

    return jsonify({
        "success": True,
        "healthy": True,
        "status": "healthy",
        "assistant": "SK 2.0",
        "backend": "Flask"
    })


# ==========================================
# COMMON AI REQUEST
# CHAT + VOICE
# ==========================================

def process_ai_request():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        # --------------------------------------
        # MESSAGE
        # --------------------------------------

        message = data.get(
            "message",
            ""
        )

        if not isinstance(
            message,
            str
        ):

            message = str(message)

        message = message.strip()

        # --------------------------------------
        # CONVERSATION
        # --------------------------------------

        conversation = data.get(
            "conversation",
            []
        )

        if not isinstance(
            conversation,
            list
        ):

            conversation = []

        # Keep only recent messages
        conversation = conversation[-20:]

        # --------------------------------------
        # VALIDATE
        # --------------------------------------

        if not message:

            return jsonify({
                "success": False,
                "error": "Message is required."
            }), 400

        # --------------------------------------
        # SAME AI BRAIN
        # --------------------------------------

        reply = ask_ai(
            message,
            conversation
        )

        # --------------------------------------
        # AI ERROR
        # --------------------------------------

        if not reply:

            return jsonify({
                "success": False,
                "error":
                    "AI provider did not respond."
            }), 503

        # --------------------------------------
        # RESPONSE
        # --------------------------------------

        return jsonify({
            "success": True,
            "reply": str(reply),
            "source": "SK 2.0 AI"
        })

    except Exception as error:

        print(
            "AI Request Error:",
            error
        )

        return jsonify({
            "success": False,
            "error": "Internal server error."
        }), 500


# ==========================================
# CHAT API
# ==========================================

@app.route(
    "/api/chat",
    methods=["POST"]
)
def chat_api():

    return process_ai_request()


# ==========================================
# VOICE API
# ==========================================

@app.route(
    "/api/voice",
    methods=["POST"]
)
def voice_api():

    return process_ai_request()


# ==========================================
# MEMORY - GET ALL
# ==========================================

@app.route(
    "/api/memory",
    methods=["GET"]
)
def get_memory_api():

    try:

        memories = get_memories()

        return jsonify({
            "success": True,
            "count": len(memories),
            "memories": memories
        })

    except Exception as error:

        print(
            "Memory GET Error:",
            error
        )

        return jsonify({
            "success": False,
            "error":
                "Could not load memories."
        }), 500


# ==========================================
# MEMORY - ADD
# ==========================================

@app.route(
    "/api/memory",
    methods=["POST"]
)
def add_memory_api():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        text = data.get(
            "text",
            ""
        )

        category = data.get(
            "category",
            "general"
        )

        # --------------------------------------
        # VALIDATE TEXT
        # --------------------------------------

        if not isinstance(
            text,
            str
        ):

            return jsonify({
                "success": False,
                "error":
                    "Memory text must be text."
            }), 400

        text = text.strip()

        if not text:

            return jsonify({
                "success": False,
                "error":
                    "Memory text is required."
            }), 400

        # --------------------------------------
        # VALIDATE CATEGORY
        # --------------------------------------

        if not isinstance(
            category,
            str
        ):

            category = "general"

        category = category.strip()

        if not category:

            category = "general"

        # --------------------------------------
        # SAVE MEMORY
        # --------------------------------------

        memory = add_memory(
            text,
            category
        )

        return jsonify({
            "success": True,
            "message":
                "Memory saved successfully.",
            "memory": memory
        }), 201

    except Exception as error:

        print(
            "Memory Add Error:",
            error
        )

        return jsonify({
            "success": False,
            "error":
                "Could not save memory."
        }), 500


# ==========================================
# MEMORY - DELETE ONE
# ==========================================

@app.route(
    "/api/memory/<int:memory_id>",
    methods=["DELETE"]
)
def delete_memory_api(memory_id):

    try:

        deleted = delete_memory(
            memory_id
        )

        if not deleted:

            return jsonify({
                "success": False,
                "error":
                    "Memory not found."
            }), 404

        return jsonify({
            "success": True,
            "message":
                "Memory deleted successfully."
        })

    except Exception as error:

        print(
            "Memory Delete Error:",
            error
        )

        return jsonify({
            "success": False,
            "error":
                "Could not delete memory."
        }), 500


# ==========================================
# MEMORY - DELETE ALL
# ==========================================

@app.route(
    "/api/memory",
    methods=["DELETE"]
)
def delete_all_memories_api():

    try:

        clear_memories()

        return jsonify({
            "success": True,
            "message":
                "All memories cleared successfully."
        })

    except Exception as error:

        print(
            "Memory Clear Error:",
            error
        )

        return jsonify({
            "success": False,
            "error":
                "Could not clear memories."
        }), 500


# ==========================================
# PC CONTROL
# ==========================================

@app.route(
    "/api/pc-control",
    methods=["POST"]
)
def pc_control():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        command = str(
            data.get(
                "command",
                ""
            )
        ).lower().strip()

        # --------------------------------------
        # SHUTDOWN
        # --------------------------------------

        if "shutdown" in command:

            os.system(
                "shutdown /s /t 5"
            )

            return jsonify({
                "success": True,
                "message":
                    "PC is shutting down."
            })

        # --------------------------------------
        # RESTART
        # --------------------------------------

        if "restart" in command:

            os.system(
                "shutdown /r /t 5"
            )

            return jsonify({
                "success": True,
                "message":
                    "PC is restarting."
            })

        # --------------------------------------
        # NOTEPAD
        # --------------------------------------

        if "notepad" in command:

            subprocess.Popen(
                ["notepad.exe"]
            )

            return jsonify({
                "success": True,
                "message":
                    "Opening Notepad."
            })

        # --------------------------------------
        # CALCULATOR
        # --------------------------------------

        if "calculator" in command:

            subprocess.Popen(
                ["calc.exe"]
            )

            return jsonify({
                "success": True,
                "message":
                    "Opening Calculator."
            })

        # --------------------------------------
        # UNKNOWN COMMAND
        # --------------------------------------

        return jsonify({
            "success": False,
            "error":
                "Unknown PC command."
        }), 400

    except Exception as error:

        print(
            "PC Control Error:",
            error
        )

        return jsonify({
            "success": False,
            "error":
                "Execution failed."
        }), 500


# ==========================================
# 404 ERROR
# ==========================================

@app.errorhandler(404)
def page_not_found(error):

    return jsonify({
        "success": False,
        "error":
            "Route not found."
    }), 404


# ==========================================
# 500 ERROR
# ==========================================

@app.errorhandler(500)
def internal_server_error(error):

    return jsonify({
        "success": False,
        "error":
            "Internal server error."
    }), 500


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":

    print("")
    print("========================================")
    print("          SK 2.0 SERVER")
    print("========================================")
    print("Assistant : SK 2.0")
    print("Backend   : Flask")
    print("Frontend  :", FRONTEND_DIR)
    print("")
    print("Server:")
    print("http://127.0.0.1:5000")
    print("")
    print("API:")
    print("GET    /api/status")
    print("GET    /api/health")
    print("POST   /api/chat")
    print("POST   /api/voice")
    print("GET    /api/memory")
    print("POST   /api/memory")
    print("DELETE /api/memory/<id>")
    print("DELETE /api/memory")
    print("POST   /api/pc-control")
    print("========================================")
    print("")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )