import warnings
from flask import Blueprint, current_app, render_template_string, url_for
from markupsafe import Markup
from utils import get_url

# defined normal file type
allowed_file_extensions = {
    "default": "image/*, audio/*, video/*, text/*, application/*",
    "image": "image/*",
    "audio": "audio/*",
    "video": "video/*",
    "text": "text/*",
    "app": "application/*",
}


class _Dropzone(object):
    @staticmethod
    def load_css(css_url=None, version="5.9.3"):
        css_filename = "dropzone.min.css"
        serve_local = current_app.config["DROPZONE_SERVE_LOCAL"]

        if serve_local:
            css = '<link rel="stylesheet" href="%s" type="text/css">\n' % url_for(
                "dropzone.static", filename=css_filename
            )
        else:
            css = (
                    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/dropzone@%s/dist/min/%s"'
                    ' type="text/css">\n' % (version, css_filename)
            )

        if css_url:
            css = '<link rel="stylesheet" href="%s" type="text/css">\n' % css_url
        return Markup(css)

    @staticmethod
    def load_js(js_url=None, version="5.9.3"):
        js_filename = "dropzone.min.js"
        serve_local = current_app.config["DROPZONE_SERVE_LOCAL"]

        if serve_local:
            js = '<script src="%s"></script>\n' % url_for(
                "dropzone.static", filename=js_filename
            )
        else:
            js = (
                    '<script src="https://cdn.jsdelivr.net/npm/dropzone@%s/dist/min/%s"></script>\n'
                    % (version, js_filename)
            )

        if js_url:
            js = '<script src="%s"></script>\n' % js_url
        return Markup(js)

    @staticmethod
    def config(redirect_url=None, custom_init="", custom_options="", nonce=None, id="myDropzone", **kwargs, ):
        if custom_init and not custom_init.strip().endswith(";"):
            custom_init += ";"

        if custom_options and not custom_options.strip().endswith(","):
            custom_options += ","

        upload_multiple = kwargs.get(
            "upload_multiple", current_app.config["DROPZONE_UPLOAD_MULTIPLE"]
        )
        parallel_uploads = kwargs.get(
            "parallel_uploads", current_app.config["DROPZONE_PARALLEL_UPLOADS"]
        )

        upload_multiple = (
            "true" if upload_multiple in [True, "true", "True", 1] else "false"
        )

        size = kwargs.get("max_file_size", current_app.config["DROPZONE_MAX_FILE_SIZE"])
        param = kwargs.get("input_name", current_app.config["DROPZONE_INPUT_NAME"])
        redirect_view = kwargs.get(
            "redirect_view", current_app.config["DROPZONE_REDIRECT_VIEW"]
        )

        if redirect_view is not None or redirect_url is not None:
            redirect_url = redirect_url or url_for(redirect_view)
            redirect_js = (
                    """
                this.on("queuecomplete", function(file) {
                // Called when all files in the queue finish uploading.
                window.location = "%s";
                });"""
                    % redirect_url
            )
        else:
            redirect_js = ""

        max_files = kwargs.get("max_files", current_app.config["DROPZONE_MAX_FILES"])

        click_upload = kwargs.get("upload_on_click", current_app.config["DROPZONE_UPLOAD_ON_CLICK"])
        button_id = kwargs.get("upload_btn_id", current_app.config["DROPZONE_UPLOAD_BTN_ID"])
        in_form = kwargs.get("in_form", current_app.config["DROPZONE_IN_FORM"])
        cancelUpload = kwargs.get("cancel_upload", current_app.config["DROPZONE_CANCEL_UPLOAD"])
        removeFile = kwargs.get("remove_file", current_app.config["DROPZONE_REMOVE_FILE"])
        cancelConfirmation = kwargs.get("cancel_confirmation", current_app.config["DROPZONE_CANCEL_CONFIRMATION"])
        uploadCanceled = kwargs.get("upload_canceled", current_app.config["DROPZONE_UPLOAD_CANCELED"])

        if click_upload:
            if in_form:
                action = get_url(
                    kwargs.get("upload_action", current_app.config["DROPZONE_UPLOAD_ACTION"])
                )

                click_listener = """
                dz = this; // Makes sure that 'this' is understood inside the functions below.

                document.getElementById("%s").addEventListener("click", function handler(e) {
                    e.currentTarget.removeEventListener(e.type, handler);
                    e.preventDefault();
                    e.stopPropagation();
                    dz.processQueue();
                });
                this.on("queuecomplete", function(file) {
                    // Called when all files in the queue finish uploading.
                    document.getElementById("%s").click();
                });
                """ % (button_id, button_id)
                click_option = (
                        """
                    url: "%s",
                    autoProcessQueue: false,
                    // addRemoveLinks: true,
                    """
                        % action
                )
            else:
                click_listener = (
                        """
                    dz = this;
                    document.getElementById("%s").addEventListener("click", function handler(e) {dz.processQueue();});
                    """
                        % button_id
                )

                click_option = """
                autoProcessQueue: false,
                // addRemoveLinks: true,
                """
            upload_multiple = "true"
            parallel_uploads = (
                max_files if isinstance(max_files, int) else parallel_uploads
            )
        else:
            click_listener = ""
            click_option = ""

        allowed_file_type = kwargs.get("allowed_file_type", current_app.config["DROPZONE_ALLOWED_FILE_TYPE"])
        allowed_file_custom = kwargs.get("allowed_file_custom", current_app.config["DROPZONE_ALLOWED_FILE_CUSTOM"])

        allowed_type = (
            allowed_file_type
            if allowed_file_custom
            else allowed_file_extensions[allowed_file_type]
        )

        default_message = kwargs.get("default_message", current_app.config["DROPZONE_DEFAULT_MESSAGE"])
        invalid_file_type = kwargs.get("invalid_file_type", current_app.config["DROPZONE_INVALID_FILE_TYPE"])
        file_too_big = kwargs.get("file_too_big", current_app.config["DROPZONE_FILE_TOO_BIG"])
        server_error = kwargs.get("server_error", current_app.config["DROPZONE_SERVER_ERROR"])
        browser_unsupported = kwargs.get("browser_unsupported", current_app.config["DROPZONE_BROWSER_UNSUPPORTED"])
        max_files_exceeded = kwargs.get("max_file_exceeded", current_app.config["DROPZONE_MAX_FILE_EXCEED"])

        timeout = kwargs.get("timeout", current_app.config["DROPZONE_TIMEOUT"])
        if timeout:
            custom_options += "timeout: %d," % timeout

        enable_csrf = kwargs.get(
            "enable_csrf", current_app.config["DROPZONE_ENABLE_CSRF"]
        )
        if enable_csrf:
            if "csrf" not in current_app.extensions:
                raise RuntimeError(
                    "CSRFProtect is not initialized. It's required to enable CSRF protect, \
                    see docs for more details."
                )
            csrf_token = render_template_string("{{ csrf_token() }}")
            custom_options += 'headers: {"X-CSRF-Token": "%s"},' % csrf_token

        nonce_html = ' nonce="%s"' % nonce if nonce else ""

        return Markup(
            """<script%s>
        Dropzone.options.%s = {
          init: function() {
              %s  // redirect after queue complete
              %s  // upload queue when button click
              %s  // custom init code
          },
          %s  // click upload options
          uploadMultiple: %s,
          parallelUploads: %d,
          paramName: "%s", // The name that will be used to transfer the file
          maxFilesize: %d, // MB
          acceptedFiles: "%s",
          maxFiles: %s,
          dictDefaultMessage: `%s`, // message display on drop area
          dictFallbackMessage: "%s",
          dictInvalidFileType: "%s",
          dictFileTooBig: "%s",
          dictResponseError: "%s",
          dictMaxFilesExceeded: "%s",
          dictCancelUpload: "%s",
          dictRemoveFile: "%s",
          dictCancelUploadConfirmation: "%s",
          dictUploadCanceled: "%s",
          %s  // custom options code
        };
        </script>
                """
            % (
                nonce_html,
                id,
                redirect_js,
                click_listener,
                custom_init,
                click_option,
                upload_multiple,
                parallel_uploads,
                param,
                size,
                allowed_type,
                max_files,
                default_message,
                browser_unsupported,
                invalid_file_type,
                file_too_big,
                server_error,
                max_files_exceeded,
                cancelUpload,
                removeFile,
                cancelConfirmation,
                uploadCanceled,
                custom_options,
            )
        )

    @staticmethod
    def create(action="", csrf=False, action_view="", id="myDropzone", **kwargs):
        if current_app.config["DROPZONE_IN_FORM"]:
            return Markup('<div class="dropzone" id="myDropzone"></div>')

        if action:
            action_url = get_url(action, **kwargs)
        else:
            warnings.warn('The argument was renamed to "action" and will be removed in 2.0.')
            action_url = url_for(action_view, **kwargs)

        if csrf:
            warnings.warn("The argument was deprecated and will be removed in 2.0, use DROPZONE_ENABLE_CSRF instead.")

        return Markup(
            f"""<form action="{action_url}" method="post" class="dropzone" id="{id}"
        enctype="multipart/form-data"></form>""")

    @staticmethod
    def style(css, id=None):
        if id is not None:
            return Markup("<style>\n.dropzone#%s{%s}\n</style>" % (id, css))
        return Markup("<style>\n.dropzone{%s}\n</style>" % css)


class Dropzone(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        blueprint = Blueprint(
            "dropzone",
            __name__,
            static_folder="static",
            static_url_path="/dropzone" + app.static_url_path,
        )
        app.register_blueprint(blueprint)

        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["dropzone"] = _Dropzone
        app.context_processor(self.context_processor)

        # settings
        app.config.setdefault("DROPZONE_SERVE_LOCAL", False)
        app.config.setdefault("DROPZONE_MAX_FILE_SIZE", 3)  # MB
        app.config.setdefault("DROPZONE_INPUT_NAME", "file")
        app.config.setdefault("DROPZONE_ALLOWED_FILE_CUSTOM", False)
        app.config.setdefault("DROPZONE_ALLOWED_FILE_TYPE", "default")
        app.config.setdefault("DROPZONE_MAX_FILES", "null")
        app.config.setdefault("DROPZONE_TIMEOUT", None)  # millisecond, default to 30000 (30 second)
        app.config.setdefault("DROPZONE_REDIRECT_VIEW", None)
        app.config.setdefault("DROPZONE_UPLOAD_MULTIPLE", False)
        app.config.setdefault("DROPZONE_PARALLEL_UPLOADS", 2)
        app.config.setdefault("DROPZONE_ENABLE_CSRF", False)
        app.config.setdefault("DROPZONE_UPLOAD_ACTION", "")
        app.config.setdefault("DROPZONE_UPLOAD_ON_CLICK", False)
        app.config.setdefault("DROPZONE_UPLOAD_BTN_ID", "upload")
        app.config.setdefault("DROPZONE_IN_FORM", False)

        # messages
        app.config.setdefault("DROPZONE_DEFAULT_MESSAGE", "Drop files here or click to upload.")
        app.config.setdefault("DROPZONE_INVALID_FILE_TYPE", "You can't upload files of this type.")
        app.config.setdefault(
            "DROPZONE_FILE_TOO_BIG",
            "File is too big {{filesize}}. Max filesize: {{maxFilesize}}MiB.",
        )
        app.config.setdefault("DROPZONE_SERVER_ERROR", "Server error: {{statusCode}}")
        app.config.setdefault(
            "DROPZONE_BROWSER_UNSUPPORTED",
            "Your browser does not support drag'n'drop file uploads.",
        )
        app.config.setdefault("DROPZONE_MAX_FILE_EXCEED", "You can't upload any more files.")
        app.config.setdefault("DROPZONE_CANCEL_UPLOAD", "Cancel upload")
        app.config.setdefault("DROPZONE_REMOVE_FILE", "Remove file")
        app.config.setdefault("DROPZONE_CANCEL_CONFIRMATION", "You really want to delete this file?")
        app.config.setdefault("DROPZONE_UPLOAD_CANCELED", "Upload canceled")

    @staticmethod
    def context_processor():
        return {"dropzone": current_app.extensions["dropzone"]}
