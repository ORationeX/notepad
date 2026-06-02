package kr.ai.lineosft.projectmanagement.api.auth.service;

import kr.ai.lineosft.projectmanagement.api.auth.dto.FindEmailRequest;
import kr.ai.lineosft.projectmanagement.api.auth.dto.FindEmailResponse;
import kr.ai.lineosft.projectmanagement.api.auth.dto.LoginRequest;
import kr.ai.lineosft.projectmanagement.api.auth.dto.ResetPasswordRequest;
import kr.ai.lineosft.projectmanagement.api.auth.dto.SignUpRequest;
import kr.ai.lineosft.projectmanagement.api.auth.dto.SignUpResponse;
import kr.ai.lineosft.projectmanagement.api.auth.dto.TokenResponse;
import kr.ai.lineosft.projectmanagement.domain.member.entity.Member;
import kr.ai.lineosft.projectmanagement.domain.member.entity.Role;
import kr.ai.lineosft.projectmanagement.domain.member.repository.MemberRepository;
import kr.ai.lineosft.projectmanagement.global.security.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final MemberRepository memberRepository;
    private final PasswordEncoder passwordEncoder;
    private final AuthenticationManager authenticationManager;
    private final JwtTokenProvider jwtTokenProvider;

    @Transactional
    @SuppressWarnings("null")
    public SignUpResponse signUp(SignUpRequest request) {
        if (memberRepository.existsByEmail(request.getEmail())) {
            throw new IllegalArgumentException("이미 가입된 이메일입니다.");
        }

        String encodedPassword = passwordEncoder.encode(request.getPassword());

        Member member = Member.builder()
                .email(request.getEmail())
                .password(encodedPassword)
                .nickname(request.getNickname())
                .phoneNumber(request.getPhoneNumber())
                .role(Role.USER)
                .build();

        Member savedMember = memberRepository.save(member);
        return SignUpResponse.from(savedMember);
    }

    @Transactional(readOnly = true)
    public TokenResponse login(LoginRequest request) {
        UsernamePasswordAuthenticationToken authenticationToken =
                new UsernamePasswordAuthenticationToken(request.getEmail(), request.getPassword());

        Authentication authentication = authenticationManager.authenticate(authenticationToken);

        String token = jwtTokenProvider.generateToken(authentication);

        return TokenResponse.of("Bearer", token);
    }

    @Transactional(readOnly = true)
    public FindEmailResponse findEmail(FindEmailRequest request) {
        Member member = memberRepository.findByNicknameAndPhoneNumber(request.getNickname(), request.getPhoneNumber())
                .orElseThrow(() -> new IllegalArgumentException("일치하는 회원 정보가 없습니다."));
        return new FindEmailResponse(member.getEmail());
    }

    @Transactional
    public void resetPassword(ResetPasswordRequest request) {
        Member member = memberRepository.findByEmailAndNicknameAndPhoneNumber(
                request.getEmail(), request.getNickname(), request.getPhoneNumber()
        ).orElseThrow(() -> new IllegalArgumentException("일치하는 회원 정보가 없습니다."));

        String encodedPassword = passwordEncoder.encode(request.getNewPassword());
        member.updatePassword(encodedPassword);
    }
}
