package kr.ai.lineosft.projectmanagement.api.project.dto;

import kr.ai.lineosft.projectmanagement.domain.project.entity.ProjectDiagram;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
public class ProjectDiagramResponse {

    private final Long id;
    private final String title;
    private final String mermaidCode;
    private final Long requirementId;
    private final Long lastModifiedByTaskId;
    private final String lastModifiedByTaskTitle;
    private final LocalDateTime createdAt;
    private final LocalDateTime updatedAt;

    public ProjectDiagramResponse(ProjectDiagram diagram) {
        this.id = diagram.getId();
        this.title = diagram.getTitle();
        this.mermaidCode = diagram.getMermaidCode();
        this.requirementId = diagram.getRequirement() != null ? diagram.getRequirement().getId() : null;
        this.lastModifiedByTaskId = diagram.getLastModifiedByTask() != null ? diagram.getLastModifiedByTask().getId() : null;
        this.lastModifiedByTaskTitle = diagram.getLastModifiedByTask() != null ? diagram.getLastModifiedByTask().getTitle() : null;
        this.createdAt = diagram.getCreatedAt();
        this.updatedAt = diagram.getUpdatedAt();
    }
}
