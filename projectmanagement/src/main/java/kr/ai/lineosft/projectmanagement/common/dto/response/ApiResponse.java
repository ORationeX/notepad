package kr.ai.lineosft.projectmanagement.common.dto.response;

import lombok.Builder;
import lombok.Getter;
import org.springframework.http.HttpStatus;

import java.time.LocalDateTime;

@Getter
public class ApiResponse<T> {
    private final boolean success;
    private final int status;
    private final String message;
    private final T data;
    private final LocalDateTime timestamp;

    @Builder
    private ApiResponse(boolean success, int status, String message, T data) {
        this.success = success;
        this.status = status;
        this.message = message;
        this.data = data;
        this.timestamp = LocalDateTime.now();
    }

    public static <T> ApiResponse<T> success(T data) {
        return ApiResponse.<T>builder()
                .success(true)
                .status(HttpStatus.OK.value())
                .message("Success")
                .data(data)
                .build();
    }

    public static <T> ApiResponse<T> success(T data, String message) {
        return ApiResponse.<T>builder()
                .success(true)
                .status(HttpStatus.OK.value())
                .message(message)
                .data(data)
                .build();
    }

    public static <T> ApiResponse<T> success(HttpStatus status, T data, String message) {
        return ApiResponse.<T>builder()
                .success(true)
                .status(status.value())
                .message(message)
                .data(data)
                .build();
    }

    public static <T> ApiResponse<T> fail(HttpStatus status, String message) {
        return ApiResponse.<T>builder()
                .success(false)
                .status(status.value())
                .message(message)
                .data(null)
                .build();
    }
}
