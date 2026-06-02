package kr.ai.lineosft.projectmanagement.api.project.dto;

import kr.ai.lineosft.projectmanagement.domain.project.entity.RequirementHistory;
import kr.ai.lineosft.projectmanagement.domain.project.entity.RequirementPriority;
import kr.ai.lineosft.projectmanagement.domain.project.entity.RequirementStatus;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
public class RequirementHistoryResponse {

    private final Long id;
    private final String title;
    private final String description;
    private final Long categoryId;
    private final String categoryName;
    private final RequirementPriority priority;
    private final String priorityDescription;
    private final RequirementStatus status;
    private final String statusDescription;
    private final Integer progress;
    private final String requestedBy;
    private final String domainName;
    private final String modifierNickname;
    private final LocalDateTime modifiedAt;
    private final String comment;

    public RequirementHistoryResponse(RequirementHistory history) {
        this.id = history.getId();
        this.title = history.getTitle();
        this.description = history.getDescription();
        this.categoryId = history.getCategory() != null ? history.getCategory().getId() : null;
        this.categoryName = history.getCategory() != null ? history.getCategory().getName() : "미지정";
        this.priority = history.getPriority();
        this.priorityDescription = history.getPriority().getDescription();
        this.status = history.getStatus();
        this.statusDescription = history.getStatus().getDescription();
        this.progress = history.getProgress();
        this.requestedBy = history.getRequestedBy();
        this.domainName = history.getDomainName();
        this.modifierNickname = history.getModifier() != null ? history.getModifier().getNickname() : "시스템";
        this.modifiedAt = history.getModifiedAt();
        this.comment = history.getComment();
    }
}
