package kr.ai.lineosft.projectmanagement.api.project.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import kr.ai.lineosft.projectmanagement.domain.project.entity.RequirementPriority;
import kr.ai.lineosft.projectmanagement.domain.project.entity.RequirementStatus;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class RequirementRequest {

    @NotBlank(message = "요구사항 제목은 필수 입력 항목입니다.")
    private String title;

    private String description;

    @NotNull(message = "요구사항 분류는 필수 입력 항목입니다.")
    private Long categoryId; // Replaces Enum Category

    private RequirementPriority priority;

    private RequirementStatus status;

    @Min(0) @Max(100)
    private Integer progress;

    private Long assigneeId;

    private String requestedBy;

    private String domainName;
}
