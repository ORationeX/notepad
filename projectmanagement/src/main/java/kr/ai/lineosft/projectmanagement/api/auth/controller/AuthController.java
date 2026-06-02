package kr.ai.lineosft.projectmanagement.api.auth.controller;

import jakarta.validation.Valid;
import kr.ai.lineosft.projectmanagement.api.auth.dto.FindEmailRequest;
import kr.ai.lineosft.projectmanagement.api.auth.dto.FindEmailResponse;
import kr.ai.lineosft.projectmanagement.api.auth.dto.LoginRequest;
import kr.ai.lineosft.projectmanagement.api.auth.dto.ResetPasswordRequest;
import kr.ai.lineosft.projectmanagement.api.auth.dto.SignUpRequest;
import kr.ai.lineosft.projectmanagement.api.auth.dto.SignUpResponse;
import kr.ai.lineosft.projectmanagement.api.auth.dto.TokenResponse;
import kr.ai.lineosft.projectmanagement.api.auth.service.AuthService;
import kr.ai.lineosft.projectmanagement.common.dto.response.ApiResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/signup")
    public ApiResponse<SignUpResponse> signUp(@Valid @RequestBody SignUpRequest request) {
        SignUpResponse response = authService.signUp(request);
        return ApiResponse.success(response, "회원가입이 완료되었습니다.");
    }

    @PostMapping("/login")
    public ApiResponse<TokenResponse> login(@Valid @RequestBody LoginRequest request) {
        TokenResponse response = authService.login(request);
        return ApiResponse.success(response, "로그인에 성공했습니다.");
    }

    @PostMapping("/find-email")
    public ApiResponse<FindEmailResponse> findEmail(@Valid @RequestBody FindEmailRequest request) {
        FindEmailResponse response = authService.findEmail(request);
        return ApiResponse.success(response, "이메일 찾기에 성공했습니다.");
    }

    @PostMapping("/reset-password")
    public ApiResponse<Void> resetPassword(@Valid @RequestBody ResetPasswordRequest request) {
        authService.resetPassword(request);
        return ApiResponse.success(null, "비밀번호가 재설정되었습니다.");
    }
}
