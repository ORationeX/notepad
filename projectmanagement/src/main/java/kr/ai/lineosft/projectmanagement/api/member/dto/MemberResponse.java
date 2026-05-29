package kr.ai.lineosft.projectmanagement.api.member.dto;

import kr.ai.lineosft.projectmanagement.domain.member.entity.Member;
import lombok.Getter;

@Getter
public class MemberResponse {
    private final Long id;
    private final String email;
    private final String nickname;

    public MemberResponse(Member member) {
        this.id = member.getId();
        this.email = member.getEmail();
        this.nickname = member.getNickname();
    }
}
