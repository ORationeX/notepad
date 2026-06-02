package kr.ai.lineosft.projectmanagement.api.member.controller;

import jakarta.validation.Valid;
import kr.ai.lineosft.projectmanagement.api.member.dto.MemberProfileResponse;
import kr.ai.lineosft.projectmanagement.api.member.dto.MemberResponse;
import kr.ai.lineosft.projectmanagement.api.member.dto.UpdateProfileRequest;
import kr.ai.lineosft.projectmanagement.common.dto.response.ApiResponse;
import kr.ai.lineosft.projectmanagement.domain.member.entity.Member;
import kr.ai.lineosft.projectmanagement.domain.member.repository.MemberRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/members")
@RequiredArgsConstructor
public class MemberApiController {

    private final MemberRepository memberRepository;
    private final PasswordEncoder passwordEncoder;

    @GetMapping
    public ResponseEntity<List<MemberResponse>> getMembers() {
        List<MemberResponse> members = memberRepository.findAll().stream()
                .map(MemberResponse::new)
                .collect(Collectors.toList());
        return ResponseEntity.ok(members);
    }

    @GetMapping("/me")
    public ApiResponse<MemberProfileResponse> getMyProfile() {
        String email = SecurityContextHolder.getContext().getAuthentication().getName();
        Member member = memberRepository.findByEmail(email)
                .orElseThrow(() -> new IllegalArgumentException("해당 이메일을 가진 사용자를 찾을 수 없습니다: " + email));
        return ApiResponse.success(new MemberProfileResponse(member), "프로필 정보를 조회했습니다.");
    }

    @PutMapping("/me")
    @Transactional
    public ApiResponse<MemberProfileResponse> updateMyProfile(@Valid @RequestBody UpdateProfileRequest request) {
        String email = SecurityContextHolder.getContext().getAuthentication().getName();
        Member member = memberRepository.findByEmail(email)
                .orElseThrow(() -> new IllegalArgumentException("해당 이메일을 가진 사용자를 찾을 수 없습니다: " + email));

        member.updateProfile(request.getNickname(), request.getPhoneNumber());

        if (request.getNewPassword() != null && !request.getNewPassword().trim().isEmpty()) {
            String newPassword = request.getNewPassword().trim();
            if (newPassword.length() < 4 || newPassword.length() > 20) {
                throw new IllegalArgumentException("비밀번호는 4자 이상 20자 이하로 입력해야 합니다.");
            }
            member.updatePassword(passwordEncoder.encode(newPassword));
        }

        memberRepository.save(member);
        return ApiResponse.success(new MemberProfileResponse(member), "회원 정보가 수정되었습니다.");
    }
}
