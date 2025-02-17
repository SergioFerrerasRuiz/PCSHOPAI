$(document).ready(function() {
    $("#chat-form").on("submit", function(e) {
        e.preventDefault();
        const loadingCircle = $("#loading-circle");
        loadingCircle.removeClass("hidden");

        const userQuestion = $("#chat-input").val().trim();
        if (userQuestion === "") {
            loadingCircle.addClass("hidden");
            return;
        }

        $("#chat-box").append(
            "<div class='message user-message'><strong>Tú:</strong> " + userQuestion + "</div>"
        );
        $("#chat-input").val("");

        $.ajax({
            type: "POST",
            url: "/ask",
            contentType: "application/json",
            data: JSON.stringify({ question: userQuestion }),
            success: function(response) {
                loadingCircle.addClass("hidden");
                if (response.answer) {
                    $("#chat-box").append(
                        "<div class='message bot-message'><div class='markdown'><strong>SERYI:</strong><br>" + response.answer + "</div></div>"
                    );
                } else {
                    $("#chat-box").append("<div class='message bot-message text-red-500'>Error en la respuesta</div>");
                }
                $("#chat-box").scrollTop($("#chat-box")[0].scrollHeight);
            },
            error: function(xhr) {
                loadingCircle.addClass("hidden");
                const errorMessage = xhr.responseJSON?.error || "Error en AJAX";
                $("#chat-box").append("<div class='message bot-message text-red-500'><strong>Error:</strong> " + errorMessage + "</div>");
            }
        });
    });

    $("#clear-chat").on("click", function() {
        $("#chat-box").empty();
    });

    // Expansión automática del textarea
    $("#chat-input").on("input", function() {
        this.style.height = "auto";
        this.style.height = (this.scrollHeight) + "px";
    });

    // Subida de archivos con indicador de carga
    $("#upload-file-btn").on("click", function() {
        $("#file-upload").click();
    });

    $("#file-upload").on("change", function() {
        const file = this.files[0];
        if (!file) return;

        const fileExtension = file.name.split('.').pop().toLowerCase();
        if (!['pdf', 'txt'].includes(fileExtension)) {
            $("#chat-box").append("<div class='message bot-message text-red-500'><strong>Error:</strong> Solo se aceptan archivos PDF o TXT.</div>");
            return;
        }

        $("#loading-circle").removeClass("hidden");
        sendFileToServer(file);
    });

    function sendFileToServer(file) {
        const formData = new FormData();
        formData.append("file", file);

        $("#chat-box").append(
            "<div class='message user-message'><strong>Tú:</strong> Enviando archivo: " + file.name + "...</div>"
        );

        $.ajax({
            type: "POST",
            url: "/upload-file",
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                $("#loading-circle").addClass("hidden");

                if (response.error) {
                    $("#chat-box").append(
                        "<div class='message bot-message text-red-500'><strong>Error:</strong> " + response.error + "</div>"
                    );
                    return;
                }

                $("#chat-box").append(
                    "<div class='message bot-message'><div class='markdown'><strong>Seryi:</strong> " + (response.summary || response.message) + "</div></div>"
                );
            },
            error: function(xhr) {
                $("#loading-circle").addClass("hidden");
                const errorMessage = xhr.responseJSON?.error || "No se pudo subir el archivo.";
                $("#chat-box").append("<div class='message bot-message text-red-500'><strong>Error:</strong> " + errorMessage + "</div>");
            },
            complete: function() {
                $("#file-upload").val("");
            }
        });
    }
});
