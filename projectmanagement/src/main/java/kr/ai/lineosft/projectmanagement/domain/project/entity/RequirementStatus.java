package kr.ai.lineosft.projectmanagement.domain.project.entity;

public enum RequirementStatus {
    DRAFT("초안"),
    REVIEWING("검토중"),
    APPROVED("승인됨"),
    DEVELOPING("개발중"),
    TESTING("테스트중"),
    COMPLETED("완료됨"),
    DEFERRED("보류");

    private final String description;

    RequirementStatus(String description) {
        this.description = description;
    }

    public String getDescription() {
        return description;
    }
}
