package kr.ai.lineosft.projectmanagement.api.auth.service;

import kr.ai.lineosft.projectmanagement.api.auth.dto.LoginRequest;
import kr.ai.lineosft.projectmanagement.api.auth.dto.SignUpRequest;
import kr.ai.lineosft.projectmanagement.api.auth.dto.SignUpResponse;
import kr.ai.lineosft.projectmanagement.api.auth.dto.TokenResponse;
import kr.ai.lineosft.projectmanagement.domain.member.entity.Member;
import kr.ai.lineosft.projectmanagement.domain.member.repository.MemberRepository;
import kr.ai.lineosft.projectmanagement.global.security.JwtTokenProvider;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

@ExtendWith(MockitoExtension.class)
class AuthServiceTest {

    @InjectMocks
    private AuthService authService;

    @Mock
    private MemberRepository memberRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @Mock
    private AuthenticationManager authenticationManager;

    @Mock
    private JwtTokenProvider jwtTokenProvider;

    @Test
    @DisplayName("회원가입 성공 - 비밀번호가 암호화되어 저장된다")
    @SuppressWarnings("null")
    void signUp_Success() {
        // given
        SignUpRequest request = new SignUpRequest();
        request.setEmail("test@example.com");
        request.setPassword("password123");
        request.setNickname("테스터");
        request.setPhoneNumber("010-1234-5678");

        given(memberRepository.existsByEmail(request.getEmail())).willReturn(false);
        given(passwordEncoder.encode(request.getPassword())).willReturn("encryptedPassword123");
        
        Member member = Member.builder()
                .email(request.getEmail())
                .password("encryptedPassword123")
                .nickname(request.getNickname())
                .phoneNumber(request.getPhoneNumber())
                .build();
        given(memberRepository.save(any(Member.class))).willReturn(member);

        // when
        SignUpResponse response = authService.signUp(request);

        // then
        assertThat(response).isNotNull();
        assertThat(response.getEmail()).isEqualTo("test@example.com");
        assertThat(response.getNickname()).isEqualTo("테스터");
        assertThat(response.getPhoneNumber()).isEqualTo("010-1234-5678");
        
        verify(memberRepository).existsByEmail(request.getEmail());
        verify(passwordEncoder).encode("password123");
        verify(memberRepository).save(any(Member.class));
    }

    @Test
    @DisplayName("회원가입 실패 - 이미 가입된 이메일인 경우 예외 발생")
    void signUp_Fail_DuplicateEmail() {
        // given
        SignUpRequest request = new SignUpRequest();
        request.setEmail("test@example.com");
        request.setPassword("password123");
        request.setNickname("테스터");
        request.setPhoneNumber("010-1234-5678");

        given(memberRepository.existsByEmail(request.getEmail())).willReturn(true);

        // when & then
        assertThatThrownBy(() -> authService.signUp(request))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("이미 가입된 이메일입니다.");
    }

    @Test
    @DisplayName("로그인 성공 - JWT 토큰이 발급된다")
    void login_Success() {
        // given
        LoginRequest request = new LoginRequest();
        request.setEmail("test@example.com");
        request.setPassword("password123");

        UsernamePasswordAuthenticationToken authenticationToken =
                new UsernamePasswordAuthenticationToken(request.getEmail(), request.getPassword());
        Authentication authentication = mock(Authentication.class);

        given(authenticationManager.authenticate(authenticationToken)).willReturn(authentication);
        given(jwtTokenProvider.generateToken(authentication)).willReturn("jwt-access-token");

        // when
        TokenResponse response = authService.login(request);

        // then
        assertThat(response).isNotNull();
        assertThat(response.getGrantType()).isEqualTo("Bearer");
        assertThat(response.getAccessToken()).isEqualTo("jwt-access-token");

        verify(authenticationManager).authenticate(authenticationToken);
        verify(jwtTokenProvider).generateToken(authentication);
    }

    @Test
    @DisplayName("로그인 실패 - 잘못된 자격 증명일 때 예외 발생")
    void login_Fail_InvalidCredential() {
        // given
        LoginRequest request = new LoginRequest();
        request.setEmail("test@example.com");
        request.setPassword("wrongpassword");

        UsernamePasswordAuthenticationToken authenticationToken =
                new UsernamePasswordAuthenticationToken(request.getEmail(), request.getPassword());

        given(authenticationManager.authenticate(authenticationToken))
                .willThrow(new BadCredentialsException("자격 증명이 올바르지 않습니다."));

        // when & then
        assertThatThrownBy(() -> authService.login(request))
                .isInstanceOf(BadCredentialsException.class);
    }
}
