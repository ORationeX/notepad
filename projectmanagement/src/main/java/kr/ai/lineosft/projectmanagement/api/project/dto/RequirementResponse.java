package kr.ai.lineosft.projectmanagement.api.project.dto;

import kr.ai.lineosft.projectmanagement.domain.project.entity.Requirement;
import kr.ai.lineosft.projectmanagement.domain.project.entity.RequirementPriority;
import kr.ai.lineosft.projectmanagement.domain.project.entity.RequirementStatus;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
public class RequirementResponse {

    private final Long id;
    private final String requirementCode;
    private final String title;
    private final String description;
    private final Long categoryId;
    private final String categoryName;
    private final RequirementPriority priority;
    private final String priorityDescription;
    private final RequirementStatus status;
    private final String statusDescription;
    private final Integer progress;
    private final Long projectId;
    private final MemberDto author;
    private final MemberDto assignee;
    private final String requestedBy;
    private final String domainName;
    private final LocalDateTime createdAt;
    private final LocalDateTime updatedAt;

    public RequirementResponse(Requirement requirement) {
        this.id = requirement.getId();
        this.requirementCode = requirement.getRequirementCode();
        this.title = requirement.getTitle();
        this.description = requirement.getDescription();
        this.categoryId = requirement.getCategory() != null ? requirement.getCategory().getId() : null;
        this.categoryName = requirement.getCategory() != null ? requirement.getCategory().getName() : "미지정";
        this.priority = requirement.getPriority();
        this.priorityDescription = requirement.getPriority().getDescription();
        this.status = requirement.getStatus();
        this.statusDescription = requirement.getStatus().getDescription();
        this.progress = requirement.getProgress();
        this.projectId = requirement.getProject().getId();
        this.author = requirement.getAuthor() != null ? new MemberDto(requirement.getAuthor()) : null;
        this.assignee = requirement.getAssignee() != null ? new MemberDto(requirement.getAssignee()) : null;
        this.requestedBy = requirement.getRequestedBy();
        this.domainName = requirement.getDomainName();
        this.createdAt = requirement.getCreatedAt();
        this.updatedAt = requirement.getUpdatedAt();
    }

    @Getter
    public static class MemberDto {
        private final Long id;
        private final String email;
        private final String nickname;

        public MemberDto(kr.ai.lineosft.projectmanagement.domain.member.entity.Member member) {
            this.id = member.getId();
            this.email = member.getEmail();
            this.nickname = member.getNickname();
        }
    }
}
