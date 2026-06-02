package kr.ai.lineosft.projectmanagement.domain.project.repository;

import kr.ai.lineosft.projectmanagement.domain.project.entity.ProjectDiagram;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface ProjectDiagramRepository extends JpaRepository<ProjectDiagram, Long> {

    @Query("SELECT pd FROM ProjectDiagram pd LEFT JOIN FETCH pd.lastModifiedByTask WHERE pd.requirement.id = :requirementId ORDER BY pd.id ASC")
    List<ProjectDiagram> findByRequirementIdWithRelations(@Param("requirementId") Long requirementId);
}
