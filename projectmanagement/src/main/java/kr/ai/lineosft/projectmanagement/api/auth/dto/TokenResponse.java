package kr.ai.lineosft.projectmanagement.api.auth.dto;

import lombok.Builder;
import lombok.Getter;

@Getter
public class TokenResponse {
    private final String grantType;
    private final String accessToken;

    @Builder
    private TokenResponse(String grantType, String accessToken) {
        this.grantType = grantType;
        this.accessToken = accessToken;
    }

    public static TokenResponse of(String grantType, String accessToken) {
        return TokenResponse.builder()
                .grantType(grantType)
                .accessToken(accessToken)
                .build();
    }
}
