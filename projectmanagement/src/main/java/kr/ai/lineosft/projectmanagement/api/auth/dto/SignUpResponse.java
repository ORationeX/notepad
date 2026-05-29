package kr.ai.lineosft.projectmanagement.api.auth.dto;

import kr.ai.lineosft.projectmanagement.domain.member.entity.Member;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
public class SignUpResponse {
    private final Long id;
    private final String email;
    private final String nickname;
    private final String phoneNumber;
    private final LocalDateTime createdAt;

    @Builder
    private SignUpResponse(Long id, String email, String nickname, String phoneNumber, LocalDateTime createdAt) {
        this.id = id;
        this.email = email;
        this.nickname = nickname;
        this.phoneNumber = phoneNumber;
        this.createdAt = createdAt;
    }

    public static SignUpResponse from(Member member) {
        return SignUpResponse.builder()
                .id(member.getId())
                .email(member.getEmail())
                .nickname(member.getNickname())
                .phoneNumber(member.getPhoneNumber())
                .createdAt(member.getCreatedAt())
                .build();
    }
}
