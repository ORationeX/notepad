package kr.ai.lineosft.projectmanagement.api.project.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class ProjectDiagramRequest {

    @NotBlank(message = "다이어그램 제목은 필수 입력 항목입니다.")
    private String title;

    @NotBlank(message = "Mermaid 코드는 필수 입력 항목입니다.")
    private String mermaidCode;

    private Long lastModifiedByTaskId;

    private Long requirementId;
}
