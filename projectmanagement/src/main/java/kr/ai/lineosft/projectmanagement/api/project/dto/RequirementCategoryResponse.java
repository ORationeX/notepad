package kr.ai.lineosft.projectmanagement.api.project.dto;

import kr.ai.lineosft.projectmanagement.domain.project.entity.RequirementCategory;
import lombok.Getter;

@Getter
public class RequirementCategoryResponse {
    private final Long id;
    private final String name;
    private final Long projectId;

    public RequirementCategoryResponse(RequirementCategory category) {
        this.id = category.getId();
        this.name = category.getName();
        this.projectId = category.getProject() != null ? category.getProject().getId() : null;
    }
}
