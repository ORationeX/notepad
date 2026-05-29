package kr.ai.lineosft.projectmanagement.common.dto.response;

import lombok.Builder;
import lombok.Getter;
import org.springframework.validation.BindingResult;
import org.springframework.validation.FieldError;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Getter
public class ErrorResponse {
    private final int status;
    private final String errorCode;
    private final String message;
    private final List<FieldErrorDetail> errors;
    private final LocalDateTime timestamp;

    @Builder
    private ErrorResponse(int status, String errorCode, String message, List<FieldErrorDetail> errors) {
        this.status = status;
        this.errorCode = errorCode;
        this.message = message;
        this.errors = errors;
        this.timestamp = LocalDateTime.now();
    }

    public static ErrorResponse of(int status, String errorCode, String message) {
        return ErrorResponse.builder()
                .status(status)
                .errorCode(errorCode)
                .message(message)
                .build();
    }

    public static ErrorResponse of(int status, String errorCode, String message, BindingResult bindingResult) {
        return ErrorResponse.builder()
                .status(status)
                .errorCode(errorCode)
                .message(message)
                .errors(FieldErrorDetail.of(bindingResult))
                .build();
    }

    @Getter
    public static class FieldErrorDetail {
        private final String field;
        private final String value;
        private final String reason;

        @Builder
        private FieldErrorDetail(String field, String value, String reason) {
            this.field = field;
            this.value = value;
            this.reason = reason;
        }

        public static List<FieldErrorDetail> of(BindingResult bindingResult) {
            List<FieldError> fieldErrors = bindingResult.getFieldErrors();
            return fieldErrors.stream()
                    .map(error -> {
                        Object rejectedValue = error.getRejectedValue();
                        return FieldErrorDetail.builder()
                                .field(error.getField())
                                .value(rejectedValue == null ? "" : rejectedValue.toString())
                                .reason(error.getDefaultMessage())
                                .build();
                    })
                    .collect(Collectors.toList());
        }
    }
}
