package kr.ai.lineosft.projectmanagement.api.member.dto;

import kr.ai.lineosft.projectmanagement.domain.member.entity.Member;
import lombok.Getter;

@Getter
public class MemberProfileResponse {
    private String email;
    private String nickname;
    private String phoneNumber;
    private String role;

    public MemberProfileResponse(Member member) {
        this.email = member.getEmail();
        this.nickname = member.getNickname();
        this.phoneNumber = member.getPhoneNumber();
        this.role = member.getRole().name();
    }
}
