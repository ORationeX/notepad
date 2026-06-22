package kr.ai.lineosft.projectmanagement.domain.project.entity;

import jakarta.persistence.*;
import kr.ai.lineosft.projectmanagement.common.entity.BaseTimeEntity;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "project_diagrams")
public class ProjectDiagram extends BaseTimeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String title;

    @Column(columnDefinition = "TEXT", nullable = false)
    private String mermaidCode;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "requirement_id", nullable = false)
    private Requirement requirement;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "last_modified_by_task_id")
    private Task lastModifiedByTask;

    @Builder
    public ProjectDiagram(String title, String mermaidCode, Requirement requirement, Task lastModifiedByTask) {
        this.title = title;
        this.mermaidCode = mermaidCode;
        this.requirement = requirement;
        this.lastModifiedByTask = lastModifiedByTask;
    }

    public void update(String title, String mermaidCode, Requirement requirement, Task lastModifiedByTask) {
        this.title = title;
        this.mermaidCode = mermaidCode;
        this.requirement = requirement;
        this.lastModifiedByTask = lastModifiedByTask;
    }
}
