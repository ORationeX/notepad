package kr.ai.lineosft.projectmanagement.domain.project.entity;

public enum RequirementPriority {
    HIGH("높음"),
    MEDIUM("보통"),
    LOW("낮음");

    private final String description;

    RequirementPriority(String description) {
        this.description = description;
    }

    public String getDescription() {
        return description;
    }
}
